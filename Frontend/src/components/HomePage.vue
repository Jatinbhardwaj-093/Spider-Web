<template>
  <div class="home-container">
    <!-- Logo in top left -->
    <div class="title-container">
      <img
        src="../resources/images/sloth_logo.png"
        alt="Sloth Reply Logo"
        class="logo-image"
      />
    </div>

    <!-- Center content area -->
    <div class="center-content">
      <div
        class="atom-container"
        :class="{ energized: isEnergized }"
        @mouseenter="onAtomHover"
        @mouseleave="onAtomLeave"
      >
        <!-- Energy field background -->
        <div class="energy-field"></div>

        <!-- Sine Wave Visualization -->
        <div class="sine-wave-container">
          <svg
            class="sine-wave-svg"
            viewBox="0 0 400 200"
            xmlns="http://www.w3.org/2000/svg"
          >
            <!-- Permanent thin outlines -->
            <path
              class="sine-outline primary-outline"
              d="M0,100 Q50,50 100,100 T200,100 T300,100 T400,100"
              fill="none"
            />
            <path
              class="sine-outline secondary-outline"
              d="M0,100 Q50,150 100,100 T200,100 T300,100 T400,100"
              fill="none"
            />
            <path
              class="sine-outline tertiary-outline"
              d="M0,100 Q25,75 50,100 T100,100 T150,100 T200,100 T250,100 T300,100 T350,100 T400,100"
              fill="none"
            />

            <!-- Thick flowing waves -->
            <path
              class="sine-wave-path primary-wave"
              d="M0,100 Q50,50 100,100 T200,100 T300,100 T400,100"
              fill="none"
            />
            <path
              class="sine-wave-path secondary-wave"
              d="M0,100 Q50,150 100,100 T200,100 T300,100 T400,100"
              fill="none"
            />
            <path
              class="sine-wave-path tertiary-wave"
              d="M0,100 Q25,75 50,100 T100,100 T150,100 T200,100 T250,100 T300,100 T350,100 T400,100"
              fill="none"
            />

            <!-- Floating particles positioned along wave paths -->
            <!-- Primary wave particles: Following main sine wave curve -->
            <circle class="sine-particle particle-1" cx="50" cy="50" r="2" />
            <circle class="sine-particle particle-2" cx="150" cy="150" r="1.8" />
            <circle class="sine-particle particle-3" cx="250" cy="50" r="1.9" />
            
            <!-- Secondary wave particles: Following inverted sine wave -->
            <circle class="sine-particle particle-4" cx="50" cy="150" r="1.7" />
            <circle class="sine-particle particle-5" cx="150" cy="50" r="1.6" />
            <circle class="sine-particle particle-6" cx="250" cy="150" r="1.8" />
            
            <!-- Tertiary wave particles: Following higher frequency wave -->
            <circle class="sine-particle particle-7" cx="75" cy="125" r="1.4" />
            <circle class="sine-particle particle-8" cx="175" cy="75" r="1.5" />
            <circle class="sine-particle particle-9" cx="275" cy="125" r="1.3" />
            <circle class="sine-particle particle-10" cx="350" cy="100" r="1.6" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Input at the bottom -->
    <div class="input-container">
      <!-- Show input wrapper always -->
      <div class="input-wrapper">
        <input
          v-model="userQuestion"
          class="question-input"
          placeholder="Ask your question here..."
          @keypress.enter="submitQuestion"
          :disabled="isLoading"
        />
        <div
          @click="submitQuestion"
          class="send-btn"
          :class="{ disabled: isLoading }"
        >
          <!-- Show loading dots when processing, otherwise show send icon -->
          <LoadingDots v-if="isLoading" />
          <img
            v-else
            src="../resources/svg/send_arrow.svg"
            alt="Send"
            class="send-icon"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LoadingDots from "./LoadingDots.vue";

export default {
  name: "HomePage",
  components: {
    LoadingDots,
  },
  data() {
    return {
      userQuestion: "",
      isLoading: false,
      isEnergized: false,
    };
  },
  methods: {
    async submitQuestion() {
      if (this.isLoading) return;

      // Start loading animation
      this.isLoading = true;

      console.log(
        "Question submitted:",
        this.userQuestion || "Testing loading animation"
      );

      try {
        // TODO: Send question to backend API
        // Simulate API call delay
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // Clear the input after successful submission
        this.userQuestion = "";
      } catch (error) {
        console.error("Error submitting question:", error);
      } finally {
        // Stop loading animation
        this.isLoading = false;
      }
    },
    onAtomHover() {
      this.isEnergized = true;
    },
    onAtomLeave() {
      this.isEnergized = false;
    },
  },
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  background: radial-gradient(
      circle at 30% 20%,
      rgba(220, 20, 60, 0.15) 0%,
      transparent 50%
    ),
    radial-gradient(
      circle at 70% 80%,
      rgba(255, 69, 0, 0.1) 0%,
      transparent 50%
    ),
    linear-gradient(
      135deg,
      #000000 0%,
      #0a0000 20%,
      #1a0505 40%,
      #0f0000 60%,
      #050000 80%,
      #000000 100%
    );
  padding: 40px 20px 40px 20px;
  position: relative;
  overflow: hidden;
}

.home-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 69, 0, 0.03),
    transparent
  );
  animation: shimmer 8s ease-in-out infinite;
  pointer-events: none;
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  50% {
    left: 100%;
  }
  100% {
    left: -100%;
  }
}

.title-container {
  position: absolute;
  top: 25px;
  left: 25px;
  z-index: 10;
  display: flex;
  align-items: center;
}

.logo-image {
  height: 80px;
  width: auto;
  max-width: 280px;
  opacity: 0.95;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4))
    drop-shadow(0 0 20px rgba(220, 20, 60, 0.1));
}

.center-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Atom container */
.atom-container {
  position: relative;
  width: 280px;
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 1000px;
  transform-style: preserve-3d;
}

/* Energy field */
.energy-field {
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    circle,
    rgba(220, 20, 60, 0.05) 0%,
    rgba(139, 0, 0, 0.03) 30%,
    transparent 70%
  );
  border-radius: 50%;
  animation: energyPulse 4s ease-in-out infinite;
}

/* Sine Wave Visualization */
.sine-wave-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  perspective: 1000px;
}

.sine-wave-svg {
  width: 500px;
  height: 250px;
  filter: drop-shadow(0 0 20px rgba(220, 20, 60, 0.3));
}

/* Permanent thin outlines */
.sine-outline {
  stroke-width: 0.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}

.primary-outline {
  stroke: rgba(220, 20, 60, 0.3);
}

.secondary-outline {
  stroke: rgba(180, 15, 45, 0.3);
}

.tertiary-outline {
  stroke: rgba(128, 128, 128, 0.3);
}

/* Thick flowing waves */
.sine-wave-path {
  stroke-width: 5;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
  animation: sineFlow 6s ease-in-out infinite;
}

.primary-wave {
  stroke: rgba(220, 20, 60, 0.9);
  stroke-width: 5;
  animation-delay: 0s;
  filter: drop-shadow(0 0 6px rgba(220, 20, 60, 0.4));
}

.secondary-wave {
  stroke: rgba(255, 140, 0, 0.8);
  stroke-width: 4;
  animation-delay: 2s;
  filter: drop-shadow(0 0 5px rgba(255, 140, 0, 0.4));
}

.tertiary-wave {
  stroke: rgba(128, 128, 128, 0.8);
  stroke-width: 3;
  animation-delay: 4s;
  filter: drop-shadow(0 0 4px rgba(128, 128, 128, 0.3));
}

.sine-particle {
  animation: particleFloat 3s ease-in-out infinite;
}

/* Primary wave particles (red) */
.particle-1 {
  fill: rgba(220, 20, 60, 0.9);
  animation-delay: 0s;
  filter: drop-shadow(0 0 4px rgba(220, 20, 60, 0.6));
}

.particle-2 {
  fill: rgba(220, 20, 60, 0.8);
  animation-delay: 0.8s;
  filter: drop-shadow(0 0 3px rgba(220, 20, 60, 0.5));
}

.particle-3 {
  fill: rgba(220, 20, 60, 0.85);
  animation-delay: 1.6s;
  filter: drop-shadow(0 0 4px rgba(220, 20, 60, 0.5));
}

/* Secondary wave particles (orange) */
.particle-4 {
  fill: rgba(255, 140, 0, 0.9);
  animation-delay: 0.5s;
  filter: drop-shadow(0 0 4px rgba(255, 140, 0, 0.6));
}

.particle-5 {
  fill: rgba(255, 140, 0, 0.8);
  animation-delay: 1.3s;
  filter: drop-shadow(0 0 3px rgba(255, 140, 0, 0.5));
}

.particle-6 {
  fill: rgba(255, 140, 0, 0.7);
  animation-delay: 2.1s;
  filter: drop-shadow(0 0 3px rgba(255, 140, 0, 0.4));
}

/* Tertiary wave particles (gray) */
.particle-7 {
  fill: rgba(128, 128, 128, 0.8);
  animation-delay: 0.3s;
  filter: drop-shadow(0 0 3px rgba(128, 128, 128, 0.5));
}

.particle-8 {
  fill: rgba(128, 128, 128, 0.7);
  animation-delay: 1.1s;
  filter: drop-shadow(0 0 2px rgba(128, 128, 128, 0.4));
}

.particle-9 {
  fill: rgba(128, 128, 128, 0.75);
  animation-delay: 1.9s;
  filter: drop-shadow(0 0 3px rgba(128, 128, 128, 0.4));
}

.particle-10 {
  fill: rgba(128, 128, 128, 0.6);
  animation-delay: 2.7s;
  filter: drop-shadow(0 0 2px rgba(128, 128, 128, 0.3));
}

.particle-7 {
  fill: rgba(139, 0, 0, 0.6);
  animation-delay: 3s;
  filter: drop-shadow(0 0 2px rgba(139, 0, 0, 0.3));
}

.particle-8 {
  fill: rgba(139, 0, 0, 0.5);
  animation-delay: 3.5s;
  filter: drop-shadow(0 0 2px rgba(139, 0, 0, 0.3));
}

.equation-display {
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 3;
}

.equation-text {
  font-family: "Courier New", monospace;
  font-size: 18px;
  color: rgba(220, 20, 60, 0.9);
  text-shadow: 0 0 10px rgba(220, 20, 60, 0.5);
  font-weight: bold;
  letter-spacing: 2px;
}

/* Enhanced animations */
@keyframes energyPulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.6;
  }
}

/* Sine wave animations */
@keyframes sineFlow {
  0% {
    stroke-dasharray: 50 50;
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dasharray: 50 50;
    stroke-dashoffset: -100;
  }
}

@keyframes particleFloat {
  0%,
  100% {
    transform: translateY(0px) scale(1);
    opacity: 0.8;
  }
  50% {
    transform: translateY(-15px) scale(1.2);
    opacity: 1;
  }
}

.input-container {
  width: 100%;
  max-width: 800px;
  flex-shrink: 0;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(220, 20, 60, 0.15);
  border-radius: 12px;
  padding: 6px;
  height: 56px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 1px 0 rgba(255, 69, 0, 0.1) inset,
    0 0 20px rgba(220, 20, 60, 0.05);
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(220, 20, 60, 0.25);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(220, 20, 60, 0.2),
    0 1px 0 rgba(255, 69, 0, 0.15) inset, 0 0 30px rgba(220, 20, 60, 0.1);
}

.question-input {
  flex: 1;
  padding: 14px 18px;
  border: none;
  background: transparent;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  color: #ffffff;
  transition: opacity 0.3s ease;
}

.question-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.question-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.send-btn {
  width: 44px;
  height: 44px;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
  padding: 10px;
}

.send-btn:hover:not(.disabled) {
  transform: scale(1.1);
}

.send-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.send-icon {
  width: 24px;
  height: 24px;
  filter: brightness(0) invert(1);
  transition: transform 0.2s ease;
}

.send-btn:hover:not(.disabled) .send-icon {
  transform: translateX(2px);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .home-container {
    padding: 32px 16px 32px 16px;
  }

  .title-container {
    top: 20px;
    left: 20px;
  }

  .logo-image {
    height: 48px;
    max-width: 160px;
  }

  .atom-container {
    width: 220px;
    height: 220px;
  }

  .sine-wave-svg {
    width: 400px;
    height: 200px;
  }

  .equation-text {
    font-size: 16px;
  }

  .input-container {
    max-width: 650px;
  }

  .input-wrapper {
    padding: 5px;
    height: 52px;
  }

  .question-input {
    padding: 12px 16px;
    font-size: 15px;
  }

  .send-btn {
    width: 42px;
    height: 42px;
    padding: 9px;
  }

  .send-icon {
    width: 22px;
    height: 22px;
  }
}

@media (max-width: 768px) {
  .home-container {
    padding: 24px 12px 24px 12px;
  }

  .title-container {
    top: 16px;
    left: 16px;
  }

  .logo-image {
    height: 42px;
    max-width: 140px;
  }

  .atom-container {
    width: 180px;
    height: 180px;
  }

  .sine-wave-svg {
    width: 350px;
    height: 175px;
  }

  .equation-text {
    font-size: 15px;
  }

  .input-container {
    max-width: 100%;
  }

  .input-wrapper {
    padding: 4px;
    border-radius: 10px;
    height: 48px;
  }

  .question-input {
    padding: 10px 14px;
    font-size: 14px;
  }

  .send-btn {
    width: 40px;
    height: 40px;
    padding: 8px;
  }

  .send-icon {
    width: 20px;
    height: 20px;
  }
}

@media (max-width: 480px) {
  .home-container {
    padding: 20px 8px 20px 8px;
  }

  .title-container {
    top: 14px;
    left: 14px;
  }

  .logo-image {
    height: 38px;
    max-width: 120px;
  }

  .atom-container {
    width: 160px;
    height: 160px;
  }

  .sine-wave-svg {
    width: 300px;
    height: 150px;
  }

  .equation-text {
    font-size: 14px;
  }

  .input-wrapper {
    padding: 3px;
    border-radius: 8px;
    height: 44px;
  }

  .question-input {
    padding: 8px 12px;
    font-size: 14px;
  }

  .send-btn {
    width: 38px;
    height: 38px;
    padding: 7px;
  }

  .send-icon {
    width: 18px;
    height: 18px;
  }
}

@media (max-width: 320px) {
  .home-container {
    padding: 16px 5px 16px 5px;
  }

  .title-container {
    top: 12px;
    left: 12px;
  }

  .logo-image {
    height: 32px;
    max-width: 100px;
  }

  .atom-container {
    width: 140px;
    height: 140px;
  }

  .sine-wave-svg {
    width: 250px;
    height: 125px;
  }

  .equation-text {
    font-size: 12px;
  }

  .input-wrapper {
    padding: 3px;
    height: 40px;
  }

  .question-input {
    padding: 6px 10px;
    font-size: 13px;
  }

  .send-btn {
    width: 34px;
    height: 34px;
    padding: 5px;
  }

  .send-icon {
    width: 16px;
    height: 16px;
  }
}

/* Large screens */
@media (min-width: 1200px) {
  .home-container {
    padding: 48px 24px 48px 24px;
  }

  .title-container {
    top: 35px;
    left: 35px;
  }

  .logo-image {
    height: 62px;
    max-width: 200px;
  }

  .atom-container {
    width: 320px;
    height: 320px;
  }

  .sine-wave-svg {
    width: 600px;
    height: 300px;
  }

  .equation-text {
    font-size: 20px;
  }

  .input-container {
    max-width: 900px;
  }

  .input-wrapper {
    padding: 8px;
    height: 60px;
  }

  .question-input {
    padding: 16px 20px;
    font-size: 16px;
  }

  .send-btn {
    width: 48px;
    height: 48px;
    padding: 12px;
  }

  .send-icon {
    width: 26px;
    height: 26px;
  }
}
</style>
