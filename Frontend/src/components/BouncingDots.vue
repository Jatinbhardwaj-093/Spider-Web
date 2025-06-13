<template>
  <div class="bouncing-dots">
    <div class="dot"></div>
    <div class="dot"></div>
    <div class="dot"></div>
  </div>
</template>

<script>
export default {
  name: "BouncingDots",
};
</script>

<style scoped>
.bouncing-dots {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 4px 0;
}

.dot {
  width: 5px;
  height: 5px;
  background: linear-gradient(135deg, #dc143c 0%, #ff4500 50%, #ff1493 100%);
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite both;
  box-shadow: 0 0 6px rgba(220, 20, 60, 0.4);
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

.dot:nth-child(3) {
  animation-delay: 0s;
}

@keyframes bounce {
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

/* Alternative pulsing animation */
@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* You can switch between animations by changing the animation property */
.dot.pulse {
  animation: pulse 1.5s ease-in-out infinite;
}
</style>
