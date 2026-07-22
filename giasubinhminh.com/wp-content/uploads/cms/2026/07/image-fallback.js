(function () {
  "use strict";

  var sitePrefix = window.location.pathname.indexOf("/giasubinhminh.com/") === 0
    ? "/giasubinhminh.com"
    : "";
  var fallbackSrc = sitePrefix + "/wp-content/uploads/cms/2026/07/banner-trung-tam-gia-su-tri-viet.png";

  function applyFallback(image) {
    if (!image || image.dataset.triVietFallback === "true") return;
    image.dataset.triVietFallback = "true";
    image.removeAttribute("srcset");
    image.removeAttribute("sizes");
    image.src = fallbackSrc;
    image.alt = image.alt || "Trung Tâm Gia Sư Trí Việt";
  }

  document.addEventListener("error", function (event) {
    if (event.target && event.target.tagName === "IMG") {
      applyFallback(event.target);
    }
  }, true);

  function repairAlreadyFailedImages() {
    Array.prototype.forEach.call(document.images, function (image) {
      if (image.complete && image.naturalWidth === 0) applyFallback(image);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", repairAlreadyFailedImages);
  } else {
    repairAlreadyFailedImages();
  }
}());
