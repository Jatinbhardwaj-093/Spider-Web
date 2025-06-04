<template>
  <div class="home-container">
    <!-- Logo in top left -->
    <div class="title-container">
      <img
        src="../resources/images/spiderWeb_logo.png"
        alt="Spider Web Reply Logo"
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

        <!-- Dynamic Spider Web Canvas -->
        <div class="spider-web-container">
          <canvas ref="spiderWebCanvas" class="spider-web-canvas"></canvas>
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
      spiderWebController: null,
      resizeObserver: null,
    };
  },
  mounted() {
    this.initSpiderWeb();
    this.setupResizeObserver();
  },
  beforeUnmount() {
    if (this.spiderWebController) {
      this.spiderWebController.destroy();
    }
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
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
      // Trigger web vibration on hover
      if (this.spiderWebController) {
        this.spiderWebController.triggerVibration();
      }
    },
    onAtomLeave() {
      this.isEnergized = false;
    },

    // Spider Web Controller Implementation
    initSpiderWeb() {
      const canvas = this.$refs.spiderWebCanvas;
      if (!canvas) return;

      this.spiderWebController = new this.SpiderWebController(canvas, this);
      this.spiderWebController.init();
    },

    setupResizeObserver() {
      if (typeof ResizeObserver !== "undefined") {
        this.resizeObserver = new ResizeObserver(() => {
          if (this.spiderWebController) {
            this.spiderWebController.resize();
          }
        });

        const container = this.$refs.spiderWebCanvas?.parentElement;
        if (container) {
          this.resizeObserver.observe(container);
        }
      }
    },

    // Color utilities adapted from original code
    createColor(min = 0) {
      // Create crimson-themed spider web colors with more variation
      const baseColors = [
        { r: 220, g: 20, b: 60 }, // Crimson
        { r: 255, g: 69, b: 0 }, // Orange Red
        { r: 139, g: 0, b: 0 }, // Dark Red
        { r: 255, g: 20, b: 147 }, // Deep Pink
        { r: 178, g: 34, b: 34 }, // Fire Brick
      ];

      const color = baseColors[Math.floor(Math.random() * baseColors.length)];
      const variance = 30;

      const r = Math.max(
        min,
        color.r + Math.floor((Math.random() - 0.5) * variance)
      );
      const g = Math.max(
        min,
        color.g + Math.floor((Math.random() - 0.5) * variance)
      );
      const b = Math.max(
        min,
        color.b + Math.floor((Math.random() - 0.5) * variance)
      );

      return {
        r: Math.min(255, r),
        g: Math.min(255, g),
        b: Math.min(255, b),
        style: `rgba(${Math.min(255, r)}, ${Math.min(255, g)}, ${Math.min(
          255,
          b
        )}, 0.8)`,
      };
    },

    d2Dist(p1, p2) {
      const dx = p1.px - p2.px;
      const dy = p1.py - p2.py;
      return Math.sqrt(dx * dx + dy * dy);
    },

    // Spider Web Controller Class Definition
    SpiderWebController: class SpiderWebController {
      constructor(canvas, component) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");
        this.component = component;
        this.objectsToDraw = [];
        this.lastRequestId = null;
        this.evolutionTimer = null;
        this.isDestroyed = false;
      }

      drawCurve(control, p1, p2, radius) {
        if (this.isDestroyed) return;
        const ctx = this.ctx;
        ctx.beginPath();
        ctx.moveTo(p1.px, p1.py);
        ctx.arcTo(control.px, control.py, p2.px, p2.py, radius);
        ctx.lineWidth = 1;
        ctx.strokeStyle = this.color.style;
        ctx.stroke();
      }

      drawLine(control, p) {
        if (this.isDestroyed) return;
        const ctx = this.ctx;
        ctx.beginPath();
        ctx.moveTo(control.px, control.py);
        ctx.lineTo(p.px, p.py);
        ctx.lineWidth = 1;
        ctx.strokeStyle = this.color.style;
        ctx.stroke();
      }

      drawNext(part) {
        if (this.isDestroyed) return;
        part.func.call(this, part.control, part.p1, part.p2, part.radius);
      }

      drawPart() {
        if (this.isDestroyed) return;

        if (this.objectsToDraw.length > 0) {
          this.lastRequestId = requestAnimationFrame(() => {
            if (!this.isDestroyed) {
              this.drawNext(this.objectsToDraw.shift());
              this.drawPart();
              // Enable subtle color animation for dynamic web
              if (Math.random() > 0.95) {
                this.color = this.component.createColor(64);
              }
            }
          });
        }
      }

      shuffleArray(target) {
        const auxArray = [];
        while (target.length > 0) {
          auxArray.push(target.shift());
        }

        while (auxArray.length > 0) {
          const n = Math.floor(Math.random() * auxArray.length);
          for (let i = 0; i < n; i++) {
            auxArray.push(auxArray.shift());
          }
          const x = auxArray.shift();
          // Create a slightly flawed/broken web (remove ~10% of strands randomly)
          if (Math.random() * 100 >= 10) {
            target.push(x);
          }
        }
      }

      drawWebByParts() {
        if (this.isDestroyed) return;

        this.ctx.clearRect(0, 0, this.screenWidth, this.screenHeight);
        const controlPoint = {
          px: this.screenWidth / 2,
          py: this.screenHeight / 2,
        };
        const outerRadius =
          Math.min(this.screenWidth / 2, this.screenHeight / 2) - 20;

        const nLines = 18; // Original number of radial lines
        const deltaAngle = 360 / nLines;
        const degree = Math.PI / 180;

        const points = [];
        for (let i = 0; i < nLines; i++) {
          points.push({
            px:
              controlPoint.px + outerRadius * Math.cos(i * deltaAngle * degree),
            py:
              controlPoint.py + outerRadius * Math.sin(i * deltaAngle * degree),
          });
        }

        const linesToDraw = [];
        for (let i = 0; i < points.length; i++) {
          linesToDraw.push({
            control: controlPoint,
            p1: points[i],
            func: this.drawLine,
          });
        }

        // Shuffle the order of lines being drawn for more natural appearance
        this.shuffleArray(linesToDraw);

        const nArcs = 18; // Original number of concentric arcs
        const dist = this.component.d2Dist(points[0], points[1]) / 2;
        const deltaRadius = dist / nArcs;

        const arcsToDraw = [];
        for (let j = 1; j <= nArcs; j++) {
          for (let i = 0; i < points.length; i++) {
            const p1 = points[i % points.length];
            const p2 = points[(i + 1) % points.length];

            arcsToDraw.push({
              control: controlPoint,
              p1: p1,
              p2: p2,
              radius: j * deltaRadius,
              func: this.drawCurve,
            });
          }
        }

        // Shuffle the order of arcs being drawn for more natural appearance
        this.shuffleArray(arcsToDraw);

        this.objectsToDraw = [];
        while (linesToDraw.length > 0) {
          this.objectsToDraw.push(linesToDraw.shift());
        }

        while (arcsToDraw.length > 0) {
          this.objectsToDraw.push(arcsToDraw.shift());
        }

        this.drawPart();
      }

      resize() {
        if (this.isDestroyed) return;

        const container = this.canvas.parentElement;
        if (!container) return;

        const rect = container.getBoundingClientRect();
        this.screenWidth = rect.width;
        this.screenHeight = rect.height;

        this.canvas.width = this.screenWidth;
        this.canvas.height = this.screenHeight;

        if (this.lastRequestId) {
          cancelAnimationFrame(this.lastRequestId);
        }

        this.drawWebByParts();
      }

      init() {
        this.color = this.component.createColor(64);
        this.resize();

        // Set up periodic redraw for evolving web animation
        this.startEvolutionTimer();
      }

      startEvolutionTimer() {
        if (this.isDestroyed) return;

        // Redraw the web every 15-25 seconds with variations
        const nextRedraw = 15000 + Math.random() * 10000;
        this.evolutionTimer = setTimeout(() => {
          if (!this.isDestroyed) {
            this.drawWebByParts();
            this.startEvolutionTimer();
          }
        }, nextRedraw);
      }

      triggerVibration() {
        if (this.isDestroyed) return;

        // Quick redraw with slight variations to simulate web vibration
        this.drawWebByParts();
      }

      destroy() {
        this.isDestroyed = true;
        if (this.lastRequestId) {
          cancelAnimationFrame(this.lastRequestId);
        }
        if (this.evolutionTimer) {
          clearTimeout(this.evolutionTimer);
        }
      }
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

/* Spider Web Visualization */
.spider-web-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(20deg);
  z-index: 2;
  perspective: 1000px;
}

.spider-web-canvas {
  width: 400px;
  height: 400px;
  filter: drop-shadow(0 0 20px rgba(220, 20, 60, 0.3));
  border-radius: 50%;
  animation: subtleRotation 120s linear infinite;
}

@keyframes subtleRotation {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
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

  .spider-web-canvas {
    width: 350px;
    height: 350px;
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

  .spider-web-canvas {
    width: 320px;
    height: 320px;
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

  .spider-web-canvas {
    width: 280px;
    height: 280px;
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

  .spider-web-canvas {
    width: 240px;
    height: 240px;
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

  .spider-web-canvas {
    width: 480px;
    height: 480px;
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
