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

const teamCarousel = document.querySelector('.team-carousel');
const teamDetail = document.querySelector('.team-detail');

if (teamCarousel && teamDetail) {
  const track = teamCarousel.querySelector('.team-track');
  const slides = teamCarousel.querySelectorAll('.team-slide');
  const prevBtn = teamCarousel.querySelector('.team-btn.prev');
  const nextBtn = teamCarousel.querySelector('.team-btn.next');
  const nameEl = teamDetail.querySelector('.team-name');
  const roleEl = teamDetail.querySelector('.team-role');
  const bioEl = teamDetail.querySelector('.team-bio');
  let currentIndex = 0;
  let autoTimer;
  const carouselInterval = 5000;

  if (slides.length <= 1) {
    teamCarousel.classList.add('is-single');
  }

  const updateDetail = (slide) => {
    if (!slide || !nameEl || !roleEl || !bioEl) {
      return;
    }
    teamDetail.classList.add('is-updating');
    window.setTimeout(() => {
      nameEl.textContent = slide.dataset.name || '';
      roleEl.textContent = slide.dataset.role || '';
      bioEl.textContent = slide.dataset.bio || '';
      teamDetail.classList.remove('is-updating');
    }, 120);
  };

  const updateCarousel = (index) => {
    if (!track || !slides.length) {
      return;
    }
    currentIndex = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === currentIndex;
      slide.classList.toggle('is-active', isActive);
      slide.setAttribute('aria-hidden', isActive ? 'false' : 'true');
    });
    updateDetail(slides[currentIndex]);
  };

  const startAuto = () => {
    if (prefersReducedMotion || slides.length <= 1) {
      return;
    }
    window.clearInterval(autoTimer);
    autoTimer = window.setInterval(() => {
      updateCarousel(currentIndex + 1);
    }, carouselInterval);
  };

  if (prevBtn && nextBtn) {
    prevBtn.addEventListener('click', () => {
      updateCarousel(currentIndex - 1);
      startAuto();
    });

    nextBtn.addEventListener('click', () => {
      updateCarousel(currentIndex + 1);
      startAuto();
    });
  }

  updateCarousel(0);
  startAuto();
}

const carouselCard = document.querySelector('.carousel-card');

if (carouselCard) {
  const track = carouselCard.querySelector('.carousel-track');
  const slides = carouselCard.querySelectorAll('.carousel-slide');
  const dots = carouselCard.querySelectorAll('.carousel-dot');
  const progressBars = carouselCard.querySelectorAll('.carousel-progress');
  const prevBtn = carouselCard.querySelector('.carousel-btn.prev');
  const nextBtn = carouselCard.querySelector('.carousel-btn.next');
  let currentIndex = 0;
  let isPaused = false;
  let autoTimer;
  let timerStart = 0;
  let remainingTime = 0;
  const carouselInterval = 9000;

  if (slides.length <= 1) {
    carouselCard.classList.add('is-single');
  }

  const clearTimer = () => {
    window.clearTimeout(autoTimer);
  };

  const scheduleTimer = (duration) => {
    if (prefersReducedMotion || slides.length <= 1) {
      return;
    }
    clearTimer();
    remainingTime = duration;
    timerStart = performance.now();
    autoTimer = window.setTimeout(() => {
      updateCarousel(currentIndex + 1);
    }, duration);
  };

  const restartProgress = () => {
    progressBars.forEach((bar, barIndex) => {
      bar.style.animation = 'none';
      bar.style.transform = 'scaleX(0)';
      void bar.offsetWidth;
      if (barIndex === currentIndex && !prefersReducedMotion) {
        bar.style.animation = `carousel-progress ${carouselInterval}ms linear forwards`;
      }
    });

    if (!isPaused) {
      scheduleTimer(carouselInterval);
    }
  };

  const updateCarousel = (index) => {
    if (!track || !slides.length) {
      return;
    }

    currentIndex = (index + slides.length) % slides.length;
    track.style.transform = `translateX(-${currentIndex * 100}%)`;

    slides.forEach((slide, slideIndex) => {
      slide.setAttribute('aria-hidden', slideIndex !== currentIndex);
    });

    dots.forEach((dot, dotIndex) => {
      dot.classList.remove('is-active');
      if (dotIndex === currentIndex) {
        dot.classList.add('is-active');
      }
    });

    restartProgress();
  };

  if (prevBtn && nextBtn) {
    prevBtn.addEventListener('click', () => {
      updateCarousel(currentIndex - 1);
    });

    nextBtn.addEventListener('click', () => {
      updateCarousel(currentIndex + 1);
    });
  }

  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      updateCarousel(index);
    });
  });

  carouselCard.addEventListener('mouseenter', () => {
    if (isPaused) {
      return;
    }
    isPaused = true;
    carouselCard.classList.add('is-paused');
    clearTimer();
    const elapsed = performance.now() - timerStart;
    remainingTime = Math.max(carouselInterval - elapsed, 0);
  });

  carouselCard.addEventListener('mouseleave', () => {
    if (!isPaused) {
      return;
    }
    isPaused = false;
    carouselCard.classList.remove('is-paused');
    scheduleTimer(remainingTime || carouselInterval);
  });

  updateCarousel(0);
}
