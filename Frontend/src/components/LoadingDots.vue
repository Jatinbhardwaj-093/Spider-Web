<template>
  <div class="loading-dots">
    <div class="dot dot-1"></div>
    <div class="dot dot-2"></div>
    <div class="dot dot-3"></div>
  </div>
</template>

<script>
export default {
  name: "LoadingDots",
};
</script>

<style scoped>
.loading-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 0;
}

.dot {
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: pulse 1.4s ease-in-out infinite both;
}

.dot-1 {
  animation-delay: -0.32s;
}

.dot-2 {
  animation-delay: -0.16s;
}

.dot-3 {
  animation-delay: 0s;
}

@keyframes pulse {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Responsive design for dots */
@media (max-width: 768px) {
  .dot {
    width: 5px;
    height: 5px;
  }

  .loading-dots {
    gap: 3px;
  }
}

@media (max-width: 480px) {
  .dot {
    width: 4px;
    height: 4px;
  }

  .loading-dots {
    gap: 2px;
  }
}
</style>
