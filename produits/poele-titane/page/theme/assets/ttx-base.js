/* Titanixxx — carrousels des sections ttx-* (délégation d'événements : rien à ré-initialiser
   sur shopify:section:load, les sections se déplacent sans casser). */
(function () {
  if (window.ttxBase) return;
  window.ttxBase = true;

  function pas(piste) {
    var premier = piste.children[0];
    if (!premier) return piste.clientWidth;
    var gap = parseFloat(getComputedStyle(piste).columnGap) || 0;
    return premier.getBoundingClientRect().width + gap;
  }

  document.addEventListener('click', function (e) {
    var bouton = e.target.closest('[data-ttx-prev], [data-ttx-next], [data-ttx-goto]');
    if (!bouton) return;
    var bloc = bouton.closest('[data-ttx-carousel]');
    if (!bloc) return;
    var piste = bloc.querySelector('[data-ttx-track]');
    if (!piste) return;
    if (bouton.hasAttribute('data-ttx-goto')) {
      var i = parseInt(bouton.getAttribute('data-ttx-goto'), 10) || 0;
      piste.scrollTo({ left: i * pas(piste), behavior: 'smooth' });
    } else {
      var sens = bouton.hasAttribute('data-ttx-next') ? 1 : -1;
      piste.scrollBy({ left: sens * pas(piste), behavior: 'smooth' });
    }
  });

  // Vignette active de la galerie produit
  document.addEventListener('scroll', function (e) {
    var piste = e.target;
    if (!piste.matches || !piste.matches('[data-ttx-track]')) return;
    var bloc = piste.closest('[data-ttx-carousel]');
    var vignettes = bloc ? bloc.querySelectorAll('[data-ttx-goto]') : [];
    if (!vignettes.length) return;
    var i = Math.round(piste.scrollLeft / pas(piste));
    vignettes.forEach(function (v, n) { v.classList.toggle('is-active', n === i); });
  }, true);
})();

/* Barre d'achat collante (mobile) : visible tant que le bouton principal n'est pas à l'écran. */
(function () {
  if (window.ttxCollant) return;
  window.ttxCollant = true;
  function init() {
    document.querySelectorAll('[data-ttx-collant]').forEach(function (barre) {
      if (barre.dataset.ttxPret) return;
      barre.dataset.ttxPret = '1';
      var section = barre.closest('.ttx-produit');
      var cta = section && section.querySelector('.ttx-produit__infos .ttx-cta');
      if (!cta || !('IntersectionObserver' in window)) { barre.hidden = true; return; }
      new IntersectionObserver(function (entrees) {
        entrees.forEach(function (e) {
          barre.hidden = e.isIntersecting;
          document.body.classList.toggle('ttx-collant-actif', !e.isIntersecting);
        });
      }).observe(cta);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  document.addEventListener('shopify:section:load', init);
})();
