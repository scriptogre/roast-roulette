/**
 * HTMX SSE Preserve Extension
 *
 * This extension works alongside the SSE extension to prevent elements marked
 * with hx-preserve from being swapped by SSE messages.
 *
 * Usage:
 * 1. Include this extension after htmx and the SSE extension
 * 2. Add hx-ext="sse-preserve" to enable the extension
 * 3. Use hx-preserve attribute to mark elements as preserved
 *
 * Example:
 * <div hx-ext="sse,sse-preserve" sse-connect="/stream">
 *   <div sse-swap="message">This will be replaced</div>
 *   <div sse-swap="message" hx-preserve>This will NOT be replaced</div>
 *   <div sse-swap="alert" hx-preserve="true">Preserved from SSE swaps</div>
 * </div>
 */

(function() {
    'use strict';

    // Debug flag - set to false to disable logging
    const DEBUG = true;
    const LOG_PREFIX = '[SSE-Preserve]';

    function log(...args) {
        if (DEBUG) {
            console.log(LOG_PREFIX, ...args);
        }
    }

    function logGroup(title, ...args) {
        if (DEBUG) {
            console.group(LOG_PREFIX + ' ' + title);
            if (args.length > 0) {
                console.log(...args);
            }
        }
    }

    function logGroupEnd() {
        if (DEBUG) {
            console.groupEnd();
        }
    }

    const PRESERVE_ATTRIBUTE = 'hx-preserve';

    function isElementPreserved(element) {
        const preserved = element && element.hasAttribute(PRESERVE_ATTRIBUTE);
        return preserved;
    }

    function isElementPreservedWithLogging(element) {
        const preserved = element && element.hasAttribute(PRESERVE_ATTRIBUTE);
        if (DEBUG && element) {
            log('Checking if element is preserved:', {
                element: element,
                tagName: element.tagName,
                id: element.id || 'no-id',
                class: element.className || 'no-class',
                preserved: preserved,
                preserveValue: preserved ? element.getAttribute(PRESERVE_ATTRIBUTE) : 'n/a'
            });
        }
        return preserved;
    }

    function getPreserveValue(element) {
        const value = element.getAttribute(PRESERVE_ATTRIBUTE) || 'true';
        log('Getting preserve value:', value, 'for element:', element);
        return value;
    }

    function findPreservedParent(element) {
        log('Searching for preserved parent of:', element);
        let parent = element.parentElement;
        let depth = 0;
        while (parent) {
            depth++;
            log(`  Checking parent at depth ${depth}:`, {
                element: parent,
                tagName: parent.tagName,
                id: parent.id || 'no-id',
                hasPreserve: parent.hasAttribute(PRESERVE_ATTRIBUTE)
            });

            if (isElementPreserved(parent)) {
                log('Found preserved parent at depth', depth, ':', parent);
                return parent;
            }
            parent = parent.parentElement;
        }
        log('No preserved parent found for:', element);
        return null;
    }

    htmx.defineExtension('sse-preserve', {

        init: function(api) {
            log('🚀 SSE Preserve Extension initialized!');
            log('Extension will prevent SSE swaps for elements with hx-preserve attribute');

            // Provide simple API for manual preservation management
            if (!window.htmxSsePreserve) {
                window.htmxSsePreserve = {
                    preserve: function(element, value = 'true') {
                        if (typeof element === 'string') {
                            element = document.querySelector(element);
                        }
                        if (element) {
                            element.setAttribute(PRESERVE_ATTRIBUTE, value);
                            log('✅ Manually preserved element:', element, 'with value:', value);
                        } else {
                            log('❌ Could not preserve element - element not found');
                        }
                    },

                    unpreserve: function(element) {
                        if (typeof element === 'string') {
                            element = document.querySelector(element);
                        }
                        if (element && isElementPreserved(element)) {
                            element.removeAttribute(PRESERVE_ATTRIBUTE);
                            log('✅ Manually unpreserved element:', element);
                        } else {
                            log('❌ Could not unpreserve element - element not found or not preserved');
                        }
                    },

                    isPreserved: function(element) {
                        if (typeof element === 'string') {
                            element = document.querySelector(element);
                        }
                        const preserved = isElementPreserved(element);
                        log('🔍 Manual check - element preserved:', preserved, 'for:', element);
                        return preserved;
                    }
                };

                log('📚 API available at window.htmxSsePreserve:', window.htmxSsePreserve);
            }
        },

        onEvent: function(name, evt) {
            // Log all events for debugging
            if (DEBUG && name.startsWith('htmx:sse')) {
                log('📨 SSE Event received:', name, evt);
            }

            // Handle SSE before message events
            if (name === 'htmx:sseBeforeMessage') {
                logGroup('🔄 Processing SSE Before Message Event');

                const target = evt.detail.elt;
                log('Target element:', {
                    element: target,
                    tagName: target?.tagName,
                    id: target?.id || 'no-id',
                    class: target?.className || 'no-class'
                });
                log('Message data preview:', evt.detail.data?.substring(0, 100) + '...');

                if (!target) {
                    log('❌ No target element found, continuing with normal processing');
                    logGroupEnd();
                    return true;
                }

                // Check if the target element is directly preserved
                if (isElementPreservedWithLogging(target)) {
                    const value = getPreserveValue(target);

                    log('🛡️ Element is DIRECTLY preserved!');
                    log('Preserve value:', value);
                    log('Preventing SSE swap...');

                    // Prevent the swap
                    evt.preventDefault();

                    // Dispatch custom event for handling preserved swaps
                    const preservedEvent = new CustomEvent('htmx:ssePreservedSwap', {
                        detail: {
                            originalEvent: evt,
                            preservedElement: target,
                            preserveValue: value,
                            messageData: evt.detail.data,
                            inherited: false
                        }
                    });

                    log('📤 Dispatching htmx:ssePreservedSwap event:', preservedEvent);
                    target.dispatchEvent(preservedEvent);

                    log('✅ SSE swap successfully prevented for directly preserved element');
                    logGroupEnd();
                    return false; // Prevent further processing
                }

                // Check if any parent elements are preserved (inheritance)
                const preservedParent = findPreservedParent(target);
                if (preservedParent) {
                    const value = getPreserveValue(preservedParent);

                    log('🛡️ Element is preserved via PARENT inheritance!');
                    log('Preserved parent:', preservedParent);
                    log('Preserve value:', value);
                    log('Preventing SSE swap...');

                    // Prevent the swap
                    evt.preventDefault();

                    // Dispatch custom event
                    const preservedEvent = new CustomEvent('htmx:ssePreservedSwap', {
                        detail: {
                            originalEvent: evt,
                            preservedElement: target,
                            preservedParent: preservedParent,
                            preserveValue: value,
                            messageData: evt.detail.data,
                            inherited: true
                        }
                    });

                    log('📤 Dispatching htmx:ssePreservedSwap event (inherited):', preservedEvent);
                    target.dispatchEvent(preservedEvent);

                    log('✅ SSE swap successfully prevented for inherited preserved element');
                    logGroupEnd();
                    return false; // Prevent further processing
                }

                log('✅ Element is NOT preserved - allowing normal SSE swap to proceed');
                logGroupEnd();
            }

            return true; // Continue with normal processing
        }
    });

    log('🎉 SSE Preserve Extension fully loaded and ready!');
    log('💡 Debugging tips:');
    log('  - Check console for [SSE-Preserve] logs');
    log('  - Listen for htmx:ssePreservedSwap events');
    log('  - Use window.htmxSsePreserve API for manual control');
    log('  - Set DEBUG = false to disable logging');

})();