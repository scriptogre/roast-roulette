from functools import partial

from copy import deepcopy

from typing import Callable, Self
import inspect
from tortoise.signals import pre_save, post_save, pre_delete, post_delete, Signals


async def call_sync_or_async(method: Callable, **kwargs):
    if inspect.iscoroutinefunction(method):
        return await method(**kwargs)
    else:
        return method(**kwargs)


class LifecycleMixin:
    """
    Add lifecycle hooks to Tortoise ORM models.

    Steps to use:
        1. Inherit from LifecycleMixin
        2. Add decorators to methods you want to run automatically

    See examples in the docstrings of each decorator.

    Available decorators:
      @before_create    - Runs before instance is created
      @after_create     - Runs after instance is created
      @before_update    - Runs before instance is updated
      @after_update     - Runs after instance is updated
      @before_delete    - Runs before instance is deleted
      @after_delete     - Runs after instance is deleted
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Skip base classes
        if cls.__name__ in ("LifecycleMixin", "Model"):
            return

        hooks: dict[str, list[Callable]] = {
            "before_create": [],
            "after_create": [],
            "before_update": [],
            "after_update": [],
            "before_delete": [],
            "after_delete": [],
        }

        # Find _run_{hook_type} flags on methods
        for method in cls.__dict__.values():
            for hook_type in hooks:
                if hasattr(method, f"_run_{hook_type}"):
                    hooks[hook_type].append(method)

        cls._connect_to_tortoise_signals(hooks)

    @classmethod
    def _connect_to_tortoise_signals(cls, hooks: dict[str, list[Callable]]):
        """
        Connect the hooks to Tortoise's signals (pre_save, post_save, pre_delete, post_delete).
        """

        if hooks["before_create"]:

            async def before_create_handler(sender, instance, using_db, update_fields):
                if instance.pk is None:  # Is being created
                    for method in hooks["before_create"]:
                        await call_sync_or_async(method, instance=instance)

            cls.register_listener(Signals.pre_save, before_create_handler)

        if hooks["after_create"]:

            async def after_create_handler(
                sender, instance, created, using_db, update_fields
            ):
                if created:  # Was created
                    for method in hooks["after_create"]:
                        await call_sync_or_async(method, instance=instance)

            cls.register_listener(Signals.post_save, after_create_handler)

        if hooks["before_update"] or hooks["after_update"]:
            # Updates are still special but follow same pattern
            async def before_update_handler(sender, instance, using_db, update_fields):
                if instance.pk is not None:
                    for method in hooks["before_update"]:
                        # field checking logic here
                        await call_sync_or_async(method, previous=deepcopy(instance))

            async def after_update_handler(
                sender, instance, created, using_db, update_fields
            ):
                if not created:
                    previous = getattr(instance, "_previous_state", None)
                    for method in hooks["after_update"]:
                        # field checking logic here
                        await call_sync_or_async(method, instance=instance)
                    if hasattr(instance, "_previous_state"):
                        del instance._previous_state

            if hooks["before_update"]:
                cls.register_listener(Signals.pre_save, before_update_handler)
            if hooks["after_update"]:
                cls.register_listener(Signals.post_save, after_update_handler)

        if hooks["before_delete"]:
            cls.register_listener(
                signal=Signals.pre_delete,
                listener=partial(
                    _call_methods_if_condition,
                    condition=True,  # Always run on delete
                    methods=hooks["before_delete"],
                ),
            )

        if hooks["after_delete"]:
            cls.register_listener(
                signal=Signals.post_delete,
                listener=partial(
                    _call_methods_if_condition,
                    condition=True,  # Always run on delete
                    methods=hooks["after_delete"],
                ),
            )

        # if hooks["before_update"]:
        #     pass
        #
        # if hooks["after_update"]:
        #     pass

        if hooks["before_update"] or hooks["after_update"]:
            # Find methods that need previous state
            methods_needing_previous = [
                method
                for method in hooks["before_update"] + hooks["after_update"]
                if getattr(method, "_need_previous_state", False)
            ]

            if hooks["before_update"]:

                @pre_save(cls)
                async def call_before_update_methods(
                    sender, instance, using_db, update_fields
                ):
                    """
                    When instance is being updated (has primary key):
                      -> Call all methods decorated with @before_update

                    Runs automatically on pre_save.
                    """

                    is_being_updated = instance.pk is not None
                    if is_being_updated:
                        if methods_needing_previous and getattr(
                            instance, "_saved_in_db", False
                        ):
                            previous_states[id(instance)] = deepcopy(instance)

                        for method in hooks["before_update"]:
                            await cls._call_update_method(
                                method, instance, previous_states.get(id(instance))
                            )

            if hooks["after_update"]:

                @post_save(cls)
                async def call_after_update_methods(
                    sender, instance, created, using_db, update_fields
                ):
                    """
                    When instance was updated (has primary key & `created` flag is False):
                      -> Call all methods decorated with @after_update

                    Runs automatically on post_save.
                    """
                    if not created:
                        previous = previous_states.pop(id(instance), None)
                        for method in hooks["after_update"]:
                            await cls._call_update_method(method, instance, previous)

            if hooks["before_delete"]:

                @pre_delete(cls)
                async def call_before_delete_methods(sender, instance, using_db):
                    """
                    When instance is being deleted:
                      -> Call all methods decorated with @before_delete

                    Runs automatically on pre_delete.
                    """

                    for method in hooks["before_delete"]:
                        await call_sync_or_async(method, instance=instance)

            if hooks["after_delete"]:

                @post_delete(cls)
                async def call_after_delete_methods(sender, instance, using_db):
                    """
                    When instance was deleted:
                      -> Call all methods decorated with @after_delete

                    Runs automatically on post_delete.
                    """

                    for method in hooks["after_delete"]:
                        await call_sync_or_async(method, instance=instance)

    @classmethod
    async def _call_update_method(cls, method, instance, previous=None):
        """Call an update method with field checking and previous state."""
        # Skip if watched fields haven't changed
        if hasattr(method, "_fields_to_watch"):
            if not any(
                instance._field_has_changed(field, previous)
                for field in method._fields_to_watch
            ):
                return

        # Pass previous instance if method wants it
        kwargs = {}
        if previous is not None and getattr(method, "_needs_previous", False):
            kwargs["previous"] = previous

        await call_sync_or_async(method, instance=instance, **kwargs)

    def _field_has_changed(
        self, field_name: str, previous_instance: Self = None
    ) -> bool:
        """Check if field changed compared to previous instance state."""

        if not previous_instance:
            return False

        # Simple field like "email"
        if "." not in field_name:
            current_value = getattr(self, field_name, None)
            previous_value = getattr(previous_instance, field_name, None)
            return current_value != previous_value

        # Nested field like "user.email"
        fk_field, related_field = field_name.split(".", 1)

        # If FK changed, related field changed too
        if self._field_has_changed(
            field_name=fk_field, previous_instance=previous_instance
        ):
            return True

        current_fk = getattr(self, fk_field, None)
        previous_fk = getattr(previous_instance, fk_field, None)

        # Same FK object? Check related field
        if current_fk and previous_fk:
            current_pk = getattr(current_fk, "pk", None)
            previous_pk = getattr(previous_fk, "pk", None)
            if current_pk == previous_pk:
                current_related = getattr(current_fk, related_field, None)
                previous_related = getattr(previous_fk, related_field, None)
                return current_related != previous_related

        return False


async def _call_methods_if_condition(
    sender,
    instance,
    using_db,
    update_fields,
    methods: list[Callable],
    condition: bool,
    created: bool = None,
):
    """Call methods if condition is True."""

    if condition:
        for method in methods:
            await call_sync_or_async(method, instance=instance)


def before_create(func: Callable) -> Callable:
    """
    Decorate method to run automatically BEFORE instance is CREATED (in database).

    Example:
        class MyModel(LifecycleMixin, Model):
            ...

            @before_create
            async def notify_before_creation(self):
                print("New instance is about to be created")
    """
    func._run_before_create = True
    return func


def after_create(func: Callable) -> Callable:
    """
    Decorate method to run automatically AFTER instance is CREATED (in database).

    Example:
        class MyModel(LifecycleMixin, Model):
            ...

            @after_create
            async def notify_after_creation(self):
                print(f'Instance was created with ID {self.id}')
    """

    func._run_after_create = True
    return func


def before_update(fields: list[str] = None) -> Callable:
    """
    Decorate method to run automatically BEFORE instance is UPDATED (in database).

    Extra features:
      - Use `fields` parameter (in decorator) to only run when specific fields change.
      - Use `previous` or `previous_self` parameter (in method) to access instance's state before any changes.

    Example:
        class Player(LifecycleMixin, Model):
            ...

            @before_update(fields=['score'])
            async def log_score_change(self, previous: Self):
                if previous.score != self.score:
                    print(f'Score changing from {previous.score} to {self.score}')
    """

    def decorator(func: Callable) -> Callable:
        func._run_before_update = True

        if fields:
            func._fields_to_watch = set(fields)

        if any(
            p in inspect.signature(func).parameters
            for p in ("previous", "previous_self")
        ):
            func._need_previous_state = True

        return func

    return decorator


def after_update(fields: list[str] = None):
    """
    Decorate method to run automatically AFTER instance is UPDATED (in database).

    Extra features:
      - Use `fields` parameter (in decorator) to only run when specific fields (including related fields, e.g. "user.email") change.
      - Use `previous` parameter (in method) to access instance's state before any changes.

    Example:
    class Player(LifecycleMixin, Model):
        ...

        @after_update(fields=["connection.is_active"])
        async def log_player_connection_changes(self, previous: Self):
            was_connected = previous.connection.is_active
            is_connected = self.connection.is_active

            match (was_connected, is_connected):
                case (True, False):
                    print(f"Player {self.name} disconnected")
                case (False, True):
                    print(f"Player {self.name} reconnected")
    """

    def decorator(func: Callable) -> Callable:
        func._run_after_update = True

        if fields:
            if not isinstance(fields, list):
                raise ValueError("fields must be list")

            func._fields_to_watch = set(fields)

        elif any(
            param in inspect.signature(func).parameters
            for param in ("previous", "previous_self")
        ):
            func._wants_previous_state = True

        return func

    return decorator


def before_delete(func: Callable) -> Callable:
    """
    Decorate method to run automatically BEFORE instance is DELETED (from database).

    Example:
        class MyModel(LifecycleMixin, Model):
            ...

            @before_delete
            async def notify_before_deletion(self):
                print(f'Instance with ID {self.id} is being deleted')
    """
    func._run_before_delete = True
    return func


def after_delete(func: Callable) -> Callable:
    """
    Decorate method to run automatically AFTER instance is DELETED (from database).

    Example:
        class MyModel(LifecycleMixin, Model):
            ...

            @after_delete
            async def notify_after_deletion(self):
                print(f'Instance with ID {self.id} was deleted')
    """
    func._run_after_delete = True
    return func
