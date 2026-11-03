/* 图片图集：按需启用 PhotoSwipe 5（MIT，assets/vendor/photoswipe/）
   页面只要有 .species-gallery 就接管；没有则 no-op；PhotoSwipe 未加载（脚本被拦/离线）
   时也只是让 <a class="gallery-item"> 按默认行为打开原图，不报错。
   署名与许可完全来自图注里的 data-* 属性（_includes/photo-card.html），
   所以一页可以同时存在多个 gallery（科/亚科/属的图片页是按种分组的）：
   灯箱按「点击时所在的 .species-gallery」分实例，图注从当前幻灯片的
   data.element 读取，不再用全局下标，避免多 gallery 串图注。 */
(function () {
  'use strict';

  var booted = false;

  function sourceLabel(url) {
    if (!url) return 'source';
    if (url.indexOf('inaturalist.org') !== -1) return 'iNaturalist';
    if (url.indexOf('commons.wikimedia.org') !== -1) return 'Wikimedia Commons';
    return 'source';
  }

  function appendLink(parent, href, label, rel) {
    var a = document.createElement('a');
    a.href = href;
    a.target = '_blank';
    a.rel = rel;
    a.textContent = label;
    parent.appendChild(a);
    return a;
  }

  function itemFromElement(el) {
    if (!el || !el.getAttribute) return null;
    return {
      credit: el.getAttribute('data-credit') || '',
      license: el.getAttribute('data-license') || '',
      licenseUrl: el.getAttribute('data-license-url') || '',
      page: el.getAttribute('data-source-page') || ''
    };
  }

  function buildCaption(item) {
    var inner = document.createElement('div');
    inner.className = 'pswp-gallery-caption-inner';

    var credit = document.createElement('span');
    credit.className = 'pswp-gallery-caption-credit';
    credit.textContent = item.credit || 'CC0 / CC BY / CC BY-SA / Public domain';
    inner.appendChild(credit);

    if (item.license) {
      inner.appendChild(document.createTextNode(' · '));
      if (item.licenseUrl) {
        appendLink(inner, item.licenseUrl, item.license, 'license noopener noreferrer');
      } else {
        inner.appendChild(document.createTextNode(item.license));
      }
    }
    if (item.page) {
      inner.appendChild(document.createTextNode(' · '));
      appendLink(inner, item.page, sourceLabel(item.page), 'noopener noreferrer');
    }
    return inner;
  }

  function boot() {
    if (booted) return;
    if (!window.PhotoSwipe || !window.PhotoSwipeLightbox) return;
    booted = true;

    var lightbox = new window.PhotoSwipeLightbox({
      gallery: '.species-gallery',
      children: 'a.gallery-item',
      pswpModule: window.PhotoSwipe,
      bgOpacity: 0.93,
      showHideAnimationType: 'zoom',
      padding: { top: 24, bottom: 56, left: 8, right: 8 }
    });

    lightbox.on('uiRegister', function () {
      lightbox.pswp.ui.registerElement({
        name: 'gallery-caption',
        className: 'pswp-gallery-caption',
        order: 9,
        isButton: false,
        appendTo: 'root',
        onInit: function (el, pswp) {
          function render() {
            if (!pswp.currSlide) return;
            var slide = pswp.currSlide;
            var item = itemFromElement(slide.data && slide.data.element);
            if (!item) item = {};
            while (el.firstChild) el.removeChild(el.firstChild);
            el.appendChild(buildCaption(item));
          }
          pswp.on('change', render);
          render();
        }
      });
    });

    lightbox.init();
  }

  function start() {
    var galleries = document.querySelectorAll('.species-gallery');
    if (!galleries.length) return;

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].isIntersecting) {
            observer.disconnect();
            boot();
            return;
          }
        }
      }, { rootMargin: '500px 0px' });
      for (var k = 0; k < galleries.length; k++) observer.observe(galleries[k]);
    }

    // pointerdown / keydown / focusin 都早于 click，交互前一定先装配好
    var events = ['pointerdown', 'touchstart', 'keydown', 'focusin'];
    for (var j = 0; j < events.length; j++) {
      document.addEventListener(events[j], boot, { passive: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
