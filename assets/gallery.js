/* 物种页图片图集：按需启用 PhotoSwipe 5（MIT，assets/vendor/photoswipe/）
   没有 .species-gallery 的页面直接 no-op；PhotoSwipe 未加载（脚本被拦/离线）时也
   只是让 <a class="gallery-item"> 按默认行为打开原图，不报错。
   署名与许可完全来自 _includes/species-gallery.html 的 data-* 属性。 */
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

  function buildCaption(item) {
    var inner = document.createElement('div');
    inner.className = 'pswp-gallery-caption-inner';

    var credit = document.createElement('span');
    credit.className = 'pswp-gallery-caption-credit';
    credit.textContent = item.credit || 'CC0 / CC BY / CC BY-SA';
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

  function boot(gallery) {
    if (booted) return;
    if (!window.PhotoSwipe || !window.PhotoSwipeLightbox) return;
    booted = true;

    var anchors = gallery.querySelectorAll('a.gallery-item');
    var items = [];
    var i;
    for (i = 0; i < anchors.length; i++) {
      items.push({
        credit: anchors[i].getAttribute('data-credit') || '',
        license: anchors[i].getAttribute('data-license') || '',
        licenseUrl: anchors[i].getAttribute('data-license-url') || '',
        page: anchors[i].getAttribute('data-source-page') || ''
      });
    }

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
            var index = pswp.currSlide.index;
            var item = items[index] || {};
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
    var gallery = document.querySelector('.species-gallery');
    if (!gallery) return;

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].isIntersecting) {
            observer.disconnect();
            boot(gallery);
            return;
          }
        }
      }, { rootMargin: '500px 0px' });
      observer.observe(gallery);
    }

    // pointerdown / keydown / focusin 都早于 click，交互前一定先装配好
    var events = ['pointerdown', 'touchstart', 'keydown', 'focusin'];
    for (var j = 0; j < events.length; j++) {
      gallery.addEventListener(events[j], function () { boot(gallery); }, { passive: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
