const revealItems = document.querySelectorAll('[data-reveal]');

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.2 }
  );

  revealItems.forEach((item) => observer.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add('is-visible'));
}

const accordionItems = document.querySelectorAll('.service-accordion details');
const closeOtherAccordionItems = (activeItem) => {
  accordionItems.forEach((other) => {
    if (other !== activeItem) {
      other.open = false;
    }
  });
};

accordionItems.forEach((item) => {
  item.addEventListener('toggle', () => {
    if (!item.open) {
      return;
    }
    closeOtherAccordionItems(item);
  });
});

const metricValues = document.querySelectorAll('.metric-value');
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const animateMetric = (metric) => {
  if (metric.dataset.animated === 'true') {
    return;
  }
  metric.dataset.animated = 'true';

  const rawTarget = metric.dataset.target ?? metric.textContent;
  const target = Number(String(rawTarget).replace(/[^0-9.-]/g, ''));
  const prefix = metric.dataset.prefix ?? '';
  const suffix = metric.dataset.suffix ?? '';

  if (!Number.isFinite(target)) {
    metric.textContent = `${prefix}${rawTarget}${suffix}`;
    return;
  }

  if (prefersReducedMotion) {
    metric.textContent = `${prefix}${target.toLocaleString('es-MX')}${suffix}`;
    return;
  }

  const duration = 1800;
  const startTime = performance.now();

  const update = (now) => {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const currentValue = Math.round(eased * target);
    metric.textContent = `${prefix}${currentValue.toLocaleString('es-MX')}${suffix}`;

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  };

  requestAnimationFrame(update);
};

if (metricValues.length) {
  const metricsSection = document.querySelector('.metrics');
  const startMetrics = () => metricValues.forEach(animateMetric);

  if ('IntersectionObserver' in window && metricsSection) {
    const metricsObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            startMetrics();
            observer.disconnect();
          }
        });
      },
      { threshold: 0.35 }
    );

    metricsObserver.observe(metricsSection);
  } else {
    startMetrics();
  }
}

const teamGallery = document.querySelector('.team-gallery');
const teamDetail = document.querySelector('.team-detail');

if (teamGallery && teamDetail) {
  const portraits = teamGallery.querySelectorAll('.team-portrait[data-name]');
  const nameEl = teamDetail.querySelector('.team-name');
  const roleEl = teamDetail.querySelector('.team-role');
  const bioEl = teamDetail.querySelector('.team-bio');

  const setActivePortrait = (portrait) => {
    if (!portrait || !nameEl || !roleEl || !bioEl) {
      return;
    }

    portraits.forEach((item) => item.classList.toggle('is-active', item === portrait));

    teamDetail.classList.add('is-updating');
    window.setTimeout(() => {
      nameEl.textContent = portrait.dataset.name || '';
      roleEl.textContent = portrait.dataset.role || '';
      bioEl.textContent = portrait.dataset.bio || '';
      teamDetail.classList.remove('is-updating');
    }, 120);
  };

  const firstPortrait = portraits[0];
  if (firstPortrait) {
    setActivePortrait(firstPortrait);
  }

  portraits.forEach((portrait) => {
    portrait.addEventListener('mouseenter', () => setActivePortrait(portrait));
    portrait.addEventListener('focus', () => setActivePortrait(portrait));
    portrait.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        setActivePortrait(portrait);
      }
    });
  });
}
