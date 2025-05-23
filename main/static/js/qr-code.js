const QRGenerator = (function() {
    const libraryExports = (function(){
        for(var r=[null,[[10,7,17,13],[1,1,1,1],[]],[[16,10,28,22],[1,1,1,1],[4,16]],[[26,15,22,18],[1,1,2,2],[4,20]],[[18,20,16,26],[2,1,4,2],[4,24]],[[24,26,22,18],[2,1,4,4],[4,28]],[[16,18,28,24],[4,2,4,4],[4,32]],[[18,20,26,18],[4,2,5,6],[4,20,36]],[[22,24,26,22],[4,2,6,6],[4,22,40]],[[22,30,24,20],[5,2,8,8],[4,24,44]],[[26,18,28,24],[5,4,8,8],[4,26,48]],[[30,20,24,28],[5,4,11,8],[4,28,52]],[[22,24,28,26],[8,4,11,10],[4,30,56]],[[22,26,22,24],[9,4,16,12],[4,32,60]],[[24,30,24,20],[9,4,16,16],[4,24,44,64]],[[24,22,24,30],[10,6,18,12],[4,24,46,68]],[[28,24,30,24],[10,6,16,17],[4,24,48,72]],[[28,28,28,28],[11,6,19,16],[4,28,52,76]],[[26,30,28,28],[13,6,21,18],[4,28,54,80]],[[26,28,26,26],[14,7,25,21],[4,28,56,84]],[[26,28,28,30],[16,8,25,20],[4,32,60,88]],[[26,28,30,28],[17,8,25,23],[4,26,48,70,92]],[[28,28,24,30],[17,9,34,23],[4,24,48,72,96]],[[28,30,30,30],[18,9,30,25],[4,28,52,76,100]],[[28,30,30,30],[20,10,32,27],[4,26,52,78,104]],[[28,26,30,30],[21,12,35,29],[4,30,56,82,108]],[[28,28,30,28],[23,12,37,34],[4,28,56,84,112]],[[28,30,30,30],[25,12,40,34],[4,32,60,88,116]],[[28,30,30,30],[26,13,42,35],[4,24,48,72,96,120]],[[28,30,30,30],[28,14,45,38],[4,28,52,76,100,124]],[[28,30,30,30],[29,15,48,40],[4,24,50,76,102,128]],[[28,30,30,30],[31,16,51,43],[4,28,54,80,106,132]],[[28,30,30,30],[33,17,54,45],[4,32,58,84,110,136]],[[28,30,30,30],[35,18,57,48],[4,28,56,84,112,140]],[[28,30,30,30],[37,19,60,51],[4,32,60,88,116,144]],[[28,30,30,30],[38,19,63,53],[4,28,52,76,100,124,148]],[[28,30,30,30],[40,20,66,56],[4,22,48,74,100,126,152]],[[28,30,30,30],[43,21,70,59],[4,26,52,78,104,130,156]],[[28,30,30,30],[45,22,74,62],[4,30,56,82,108,134,160]],[[28,30,30,30],[47,24,77,65],[4,24,52,80,108,136,164]],[[28,30,30,30],[49,25,81,68],[4,28,56,84,112,140,168]]],t=/^\d*$/,e=/^[A-Za-z0-9 $%*+\-./:]*$/,n=/^[A-Z0-9 $%*+\-./:]*$/,a=[],o=[-1],u=0,f=1;u<255;++u)a.push(f),o[f]=u,f=2*f^(f>=128?285:0);var i=[[]];for(u=0;u<30;++u){for(var s=i[u],h=[],l=0;l<=u;++l){var c=l<u?a[s[l]]:0,v=a[(u+(s[l-1]||0))%255];h.push(o[c^v])}i.push(h)}var g={};for(u=0;u<45;++u)g["0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:".charAt(u)]=u;var p=[function(r,t){return(r+t)%2==0},function(r,t){return r%2==0},function(r,t){return t%3==0},function(r,t){return(r+t)%3==0},function(r,t){return((r/2|0)+(t/3|0))%2==0},function(r,t){return r*t%2+r*t%3==0},function(r,t){return(r*t%2+r*t%3)%2==0},function(r,t){return((r+t)%2+r*t%3)%2==0}],d=function(r){return r>6},m=function(t,e){var n=-8&function(t){var e=r[t],n=16*t*t+128*t+64;return d(t)&&(n-=36),e[2].length&&(n-=25*e[2].length*e[2].length-10*e[2].length-55),n}(t),a=r[t];return n-=8*a[0][e]*a[1][e]},w=function(r,t){switch(t){case 1:return r<10?10:r<27?12:14;case 2:return r<10?9:r<27?11:13;case 4:return r<10?8:16;case 8:return r<10?8:r<27?10:12}},b=function(r,t,e){var n=m(r,e)-4-w(r,t);switch(t){case 1:return 3*(n/10|0)+(n%10<4?0:n%10<7?1:2);case 2:return 2*(n/11|0)+(n%11<6?0:1);case 4:return n/8|0;case 8:return n/13|0}},x=function(r,t){for(var e=r.slice(0),n=r.length,u=t.length,f=0;f<u;++f)e.push(0);for(f=0;f<n;){var i=o[e[f++]];if(i>=0)for(var s=0;s<u;++s)e[f+s]^=a[(i+t[s])%255]}return e.slice(n)},y=function(r,t,e,n){for(var a=r<<n,o=t-1;o>=0;--o)a>>n+o&1&&(a^=e<<o);return r<<n|a},A=function(r,t,e){for(var n=p[e],a=r.length,o=0;o<a;++o)for(var u=0;u<a;++u)t[o][u]||(r[o][u]^=n(o,u));return r},M=function(r,t,e,n){for(var a=r.length,o=21522^y(e<<3|n,5,1335,10),u=0;u<15;++u){var f=[a-1,a-2,a-3,a-4,a-5,a-6,a-7,a-8,7,5,4,3,2,1,0][u];r[[0,1,2,3,4,5,7,8,a-7,a-6,a-5,a-4,a-3,a-2,a-1][u]][8]=r[8][f]=o>>u&1}return r},C=function(r){for(var t=function(r){for(var t=0,e=0;e<r.length;++e)r[e]>=5&&(t+=r[e]-5+3);for(e=5;e<r.length;e+=2){var n=r[e];r[e-1]==n&&r[e-2]==3*n&&r[e-3]==n&&r[e-4]==n&&(r[e-5]>=4*n||r[e+1]>=4*n)&&(t+=40)}return t},e=r.length,n=0,a=0,o=0;o<e;++o){var u,f=r[o];u=[0];for(var i=0;i<e;){for(s=0;i<e&&f[i];++s)++i;for(u.push(s),s=0;i<e&&!f[i];++s)++i;u.push(s)}n+=t(u),u=[0];for(i=0;i<e;){var s;for(s=0;i<e&&r[i][o];++s)++i;for(u.push(s),s=0;i<e&&!r[i][o];++s)++i;u.push(s)}n+=t(u);var h=r[o+1]||[];a+=f[0];for(i=1;i<e;++i){var l=f[i];a+=l,f[i-1]==l&&h[i]===l&&h[i-1]===l&&(n+=3)}}return n+=10*(Math.abs(a/e/e-.5)/.05|0)},L=function(t,e,n,a,o){var u=r[e],f=function(r,t,e,n){var a=[],o=0,u=8,f=e.length,i=function(r,t){if(t>=u){for(a.push(o|r>>(t-=u));t>=8;)a.push(r>>(t-=8)&255);o=0,u=8}t>0&&(o|=(r&(1<<t)-1)<<(u-=t))},s=w(r,t);switch(i(t,4),i(f,s),t){case 1:for(var h=2;h<f;h+=3)i(parseInt(e.substring(h-2,h+1),10),10);i(parseInt(e.substring(h-2),10),[0,4,7][f%3]);break;case 2:for(h=1;h<f;h+=2)i(45*g[e.charAt(h-1)]+g[e.charAt(h)],11);f%2==1&&i(g[e.charAt(h-1)],6);break;case 4:for(h=0;h<f;++h)i(e[h],8)}for(i(0,4),u<8&&a.push(o);a.length+1<n;)a.push(236,17);return a.length<n&&a.push(236),a}(e,n,t,m(e,a)>>3);f=function(r,t,e){for(var n=[],a=r.length/t|0,o=0,u=t-r.length%t,f=0;f<u;++f)n.push(o),o+=a;for(f=u;f<t;++f)n.push(o),o+=a+1;n.push(o);var i=[];for(f=0;f<t;++f)i.push(x(r.slice(n[f],n[f+1]),e));var s=[],h=r.length/t|0;for(f=0;f<h;++f)for(var l=0;l<t;++l)s.push(r[n[l]+f]);for(l=u;l<t;++l)s.push(r[n[l+1]-1]);for(f=0;f<e.length;++f)for(l=0;l<t;++l)s.push(i[l][f]);return s}(f,u[1][a],i[u[0][a]]);var s=function(t){for(var e=r[t],n=function(r){return 4*r+17}(t),a=[],o=[],u=0;u<n;++u)a.push([]),o.push([]);var f=function(r,t,e,n,u){for(var f=0;f<e;++f)for(var i=0;i<n;++i)a[r+f][t+i]=u[f]>>i&1,o[r+f][t+i]=1};for(f(0,0,9,9,[127,65,93,93,93,65,383,0,64]),f(n-8,0,8,9,[256,127,65,93,93,93,65,127]),f(0,n-8,9,8,[254,130,186,186,186,130,254,0,0]),u=9;u<n-8;++u)a[6][u]=a[u][6]=1&~u,o[6][u]=o[u][6]=1;var i=e[2],s=i.length;for(u=0;u<s;++u)for(var h=0==u?s-1:s,l=0==u||u==s-1?1:0;l<h;++l)f(i[u],i[l],5,5,[31,17,21,17,31]);if(d(t)){var c=y(t,6,7973,12),v=0;for(u=0;u<6;++u)for(l=0;l<3;++l)a[u][n-11+l]=a[n-11+l][u]=c>>v++&1,o[u][n-11+l]=o[n-11+l][u]=1}return{matrix:a,reserved:o}}(e),h=s.matrix,l=s.reserved;if(function(r,t,e){for(var n=r.length,a=0,o=-1,u=n-1;u>=0;u-=2){6==u&&--u;for(var f=o<0?n-1:0,i=0;i<n;++i){for(var s=u;s>u-2;--s)t[f][s]||(r[f][s]=e[a>>3]>>(7&~a)&1,++a);f+=o}o=-o}}(h,l,f),o<0){A(h,l,0),M(h,0,a,0);var c=0,v=C(h);for(A(h,l,0),o=1;o<8;++o){A(h,l,o),M(h,0,a,o);var p=C(h);v>p&&(v=p,c=o),A(h,l,o)}o=c}return A(h,l,o),M(h,0,a,o),h},k={generate:function(r,a){var o={numeric:1,alphanumeric:2,octet:4},u={L:1,M:0,Q:3,H:2},f=(a=a||{}).version||-1,i=u[(a.ecclevel||"L").toUpperCase()],s=a.mode?o[a.mode.toLowerCase()]:-1,h="mask"in a?a.mask:-1;if(s<0)s="string"==typeof r?r.match(t)?1:r.match(n)?2:4:4;else if(1!=s&&2!=s&&4!=s)throw"invalid or unsupported mode";if(r=function(r,n){switch(r){case 1:return n.match(t)?n:null;case 2:return n.match(e)?n.toUpperCase():null;case 4:if("string"==typeof n){for(var a=[],o=0;o<n.length;++o){var u=n.charCodeAt(o);u<128?a.push(u):u<2048?a.push(192|u>>6,128|63&u):u<65536?a.push(224|u>>12,128|u>>6&63,128|63&u):a.push(240|u>>18,128|u>>12&63,128|u>>6&63,128|63&u)}return a}return n}}(s,r),null===r)throw"invalid data format";if(i<0||i>3)throw"invalid ECC level";if(f<0){for(f=1;f<=40&&!(r.length<=b(f,s,i));++f);if(f>40)throw"too large data"}else if(f<1||f>40)throw"invalid version";if(-1!=h&&(h<0||h>8))throw"invalid mask";return L(r,f,s,i,h)},generateHTML:function(r,t){t=t||{};for(var e=k.generate(r,t),n=Math.max(t.modulesize||5,.5),a=t.unit||"px",o=t.ratio||1,u=Math.max(null!==t.margin?t.margin:4,0),f=document.createElement("div"),i=e.length,s=['<table border="0" cellspacing="0" cellpadding="0" style="border:'+n*u+'px solid #fff;background:#fff">'],h=0;h<i;++h){s.push("<tr>");for(var l=0;l<i;++l){const r="px"!==a?"width:"+n*o+a+"; height:"+n*o+a:"width:"+n+"px;height:"+n+"px";s.push('<td style="'+r+(e[h][l]?";background:#000":"")+'" part="'+(e[h][l]?"module-fg":"module-bg")+'" ></td>')}s.push("</tr>")}return f.className="qrcode",f.innerHTML=s.join("")+"</table>",f},generateSVG:function(r,t){t=t||{};var e=k.generate(r,t),n=e.length,a=Math.max(t.modulesize||5,.5),o=Math.max(null!==t.margin?t.margin:4,0),u=a*(n+2*o),f=' class= "fg" width="'+a+'" height="'+a+'"/>',i=document.createElementNS("http://www.w3.org/2000/svg","svg");i.setAttribute("viewBox","0 0 "+u+" "+u),i.setAttribute("style","shape-rendering:crispEdges"),t.modulesize&&(i.setAttribute("width",u),i.setAttribute("height",u));for(var s=["<style scoped>.bg{fill:transparent}.fg{fill:#000}</style>",'<rect class="bg" x="0" y="0"','width="'+u+'" height="'+u+'"/>'],h=o*a,l=0;l<n;++l){for(var c=o*a,v=0;v<n;++v)e[l][v]&&s.push('<rect x="'+c+'" y="'+h+'"',f),c+=a;h+=a}return i.innerHTML=s.join(""),i},generatePNG:function(r,t){t=t||{};var e,n=k.generate(r,t),a=Math.max(t.modulesize||5,.5),o=Math.max(null!==t.margin?t.margin:4,0),u=n.length,f=a*(u+2*o),i=document.createElement("canvas");if(i.width=i.height=f,!(e=i.getContext("2d")))throw"canvas support is needed for PNG output";e.fillStyle="#fff",e.fillRect(0,0,f,f),e.fillStyle="#000";for(var s=0;s<u;++s)for(var h=0;h<u;++h)n[s][h]&&e.fillRect(a*(o+h),a*(o+s),a,a);return i.toDataURL()}};

        return k;
    })();

    if (typeof libraryExports === 'undefined' || typeof libraryExports.generateSVG !== 'function') {
        console.error("Failed to embed or execute the QR Code library correctly.");
        return { generatePNG: ()=>{}, generateHTML: ()=>{}, generateSVG: ()=>{} };
    }

    return libraryExports;

})();

class QRCodeElement extends HTMLElement {

    constructor() {
        super()
        this._defineProperty = this._defineProperty.bind(this)
        this.attachShadow({ mode: 'open' })

        const style = document.createElement('style');
        style.textContent = `
            :host {
                display: block; /* Or inline-block */
                width: 10em; /* Default size */
                height: 10em;
                color: inherit; /* Inherit color from parent */
                line-height: 0; /* Prevent extra space */
            }
            svg {
                display: block; /* Prevent extra space inside */
                width: 100%;
                height: 100%;
            }
        `;
        this.shadowRoot.appendChild(style);

        Object.keys(QRCodeElement.defaultAttributes).map(this._defineProperty)
    }

    static get defaultAttributes() {
        return {
            content: null,
            format: 'svg',
            modulesize: 5,
            margin: 0,
            ecclevel: 'L'
        }
    }

    static get observedAttributes() {
        return Object.keys(QRCodeElement.defaultAttributes)
    }

    connectedCallback() {
        if (!this.hasAttribute('content')) {
            this.shadowRoot.textContent = 'qr-code: waiting for content attribute...';
        } else if (this.content) {
            requestAnimationFrame(() => this.generate());
        }
    }

    attributeChangedCallback(attributeName, oldValue, newValue) {
        if (oldValue === newValue) return;

        const fn = this[attributeName+'Changed'];
        if (fn && typeof fn === 'function') {
            fn.call(this, oldValue, newValue);
        }

        if (this.content) {
            this.generate();
        } else {
            this.clear();
            this.shadowRoot.textContent = 'qr-code: no content!';
        }
    }

    _defineProperty(attributeName) {
        Object.defineProperty(this, attributeName, {
            get: () => {
                const value = this.getAttribute(attributeName);
                return value === null ? QRCodeElement.defaultAttributes[attributeName] : value;
            },
            set: value => {
                if (value !== null && value !== undefined) {
                    this.setAttribute(attributeName, value);
                } else {
                    this.removeAttribute(attributeName);
                }
            }
        })
    }

    getOptions() {
        const options = {
            margin: this.margin !== null ? parseInt(this.margin, 10) : QRCodeElement.defaultAttributes.margin,
            modulesize: this.modulesize !== null ? parseInt(this.modulesize, 10) : QRCodeElement.defaultAttributes.modulesize,
            ecclevel: this.ecclevel || QRCodeElement.defaultAttributes.ecclevel
        };
        Object.keys(options).forEach(key => (options[key] == null) && delete options[key]);
        return options;
    }

    generate() {
        clearTimeout(this._generateTimeout);
        this._generateTimeout = setTimeout(() => {
            requestAnimationFrame(() => {
                if (!this.content) {
                    this.clear();
                    this.shadowRoot.textContent = 'qr-code: no content!';
                    return;
                }
                try {
                    this.clear();
                    const options = this.getOptions();
                    const contentValue = this.content;

                    this.generateSVG(contentValue, options);
                } catch (e) {
                    console.error("QR Code generation failed:", e);
                    this.shadowRoot.textContent = `qr-code: error generating! ${e.message}`;
                }
            });
        }, 0);
    }

    generateSVG(content, options) {
        const svg = QRGenerator.generateSVG(content, options);

        const styleElement = svg.querySelector('style');
        if (styleElement) {
            let styleContent = styleElement.textContent;
            styleContent = styleContent.replace(/#000/g, 'currentColor');
            styleContent = styleContent.replace(/#FFF/g, 'transparent');
            styleElement.textContent = styleContent;
        } else {
            console.warn('QR Code SVG generator did not produce expected <style> tag. Color inheritance might not work.');
        }

        svg.setAttribute('part', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

        this.shadowRoot.appendChild(svg);
    }

    clear() {
        while (this.shadowRoot.lastChild) {
            this.shadowRoot.removeChild(this.shadowRoot.lastChild);
        }
    }
}

customElements.define('qr-code', QRCodeElement);
