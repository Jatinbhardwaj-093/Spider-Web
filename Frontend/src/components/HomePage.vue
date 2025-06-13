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
    <div class="center-content" v-if="chatMessages.length === 0">
      <div
        class="atom-container"
        :class="{ energized: isEnergized }"
        @mouseenter="onAtomHover"
        @mouseleave="onAtomLeave"
      >
        <!-- Sine Curve Container -->
        <div class="sine-curve-container">
          <svg
            class="sine-curve-svg"
            viewBox="0 0 400 400"
            xmlns="http://www.w3.org/2000/svg"
          >
            <!-- Gradient definitions -->
            <defs>
              <linearGradient
                id="sineGradient"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="0%"
              >
                <stop
                  offset="0%"
                  style="stop-color: #dc143c; stop-opacity: 1"
                />
                <stop
                  offset="25%"
                  style="stop-color: #ff4500; stop-opacity: 1"
                />
                <stop
                  offset="50%"
                  style="stop-color: #ff1493; stop-opacity: 1"
                />
                <stop
                  offset="75%"
                  style="stop-color: #ff4500; stop-opacity: 1"
                />
                <stop
                  offset="100%"
                  style="stop-color: #dc143c; stop-opacity: 1"
                />
              </linearGradient>
              <linearGradient id="sineGlow" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop
                  offset="0%"
                  style="stop-color: #dc143c; stop-opacity: 0.3"
                />
                <stop
                  offset="50%"
                  style="stop-color: #ff1493; stop-opacity: 0.6"
                />
                <stop
                  offset="100%"
                  style="stop-color: #dc143c; stop-opacity: 0.3"
                />
              </linearGradient>
            </defs>

            <!-- Background glow -->
            <path
              class="sine-glow"
              d="M30 200 Q65 140, 100 200 T170 200 T240 200 T310 200 T370 200"
              stroke="url(#sineGlow)"
              stroke-width="12"
              fill="none"
              stroke-linecap="round"
            />

            <!-- Main sine curve -->
            <path
              class="sine-curve"
              d="M30 200 Q65 140, 100 200 T170 200 T240 200 T310 200 T370 200"
              stroke="url(#sineGradient)"
              stroke-width="4"
              fill="none"
              stroke-linecap="round"
            />

            <!-- Animated dots along the curve -->
            <circle class="sine-dot sine-dot-1" r="6" fill="url(#sineGradient)">
              <animateMotion dur="4s" repeatCount="indefinite">
                <mpath href="#sinePath" />
              </animateMotion>
            </circle>
            <circle
              class="sine-dot sine-dot-2"
              r="5"
              fill="rgba(255, 69, 0, 0.8)"
            >
              <animateMotion dur="4s" repeatCount="indefinite" begin="1s">
                <mpath href="#sinePath" />
              </animateMotion>
            </circle>
            <circle
              class="sine-dot sine-dot-3"
              r="4"
              fill="rgba(255, 20, 147, 0.8)"
            >
              <animateMotion dur="4s" repeatCount="indefinite" begin="2s">
                <mpath href="#sinePath" />
              </animateMotion>
            </circle>

            <!-- Hidden path for animation -->
            <path
              id="sinePath"
              d="M30 200 Q65 140, 100 200 T170 200 T240 200 T310 200 T370 200"
              stroke="none"
              fill="none"
            />
          </svg>
        </div>
      </div>
    </div>

    <!-- Chat Messages Area -->
    <div
      class="chat-container"
      v-if="chatMessages.length > 0"
      :class="{ 'full-height': chatMessages.length > 0 }"
    >
      <div class="chat-messages" ref="chatMessages">
        <div
          v-for="(message, index) in chatMessages"
          :key="index"
          class="message-wrapper"
          :class="{
            'user-message': message.type === 'user',
            'ai-message': message.type === 'ai',
          }"
        >
          <div class="message-bubble">
            <div v-if="message.image" class="message-image-container">
              <div class="image-label">Image:</div>
              <img
                :src="'data:image/jpeg;base64,' + message.image"
                alt="User uploaded image"
                class="message-image"
              />
            </div>
            <div v-if="message.text" class="message-text">
              {{ message.text }}
            </div>
            <div v-if="message.answer" class="message-text">
              {{ message.answer }}
            </div>
            <div v-if="message.isLoading" class="message-loading">
              <BouncingDots />
            </div>
            <div
              v-if="message.links && message.links.length > 0"
              class="message-links"
            >
              <div class="links-header">Related Links:</div>
              <div class="links-list">
                <a
                  v-for="(link, linkIndex) in message.links"
                  :key="linkIndex"
                  :href="link.url"
                  target="_blank"
                  class="message-link-item"
                >
                  <svg
                    class="link-icon"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M10 6H6C4.89543 6 4 6.89543 4 8V18C4 19.1046 4.89543 20 6 20H16C17.1046 20 18 19.1046 18 18V14M14 4H20M20 4V10M20 4L10 14"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  <div class="link-content">
                    <span class="link-title">{{
                      link.text || link.title
                    }}</span>
                    <span class="link-url">{{ link.url }}</span>
                  </div>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input at the bottom -->
    <div class="input-container">
      <!-- Base64 image input area (appears when picture button is clicked) -->
      <div
        v-if="showImageInput"
        class="base64-input-container"
        :style="base64ContainerStyle"
      >
        <div class="base64-input-header">
          <span class="base64-label">Paste Base64 Image:</span>
          <button
            @click="closeImageInput"
            class="close-input-btn"
            title="Close image input"
          >
            <svg
              class="close-icon"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M18 6L6 18M6 6L18 18"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
        </div>
        <input
          v-model="base64Input"
          class="base64-input"
          type="text"
          placeholder="Paste your base64 encoded image here..."
        />
        <div class="base64-input-actions">
          <button @click="clearBase64" class="clear-base64-btn">Clear</button>
          <span v-if="base64Input" class="base64-status">{{
            getBase64Status()
          }}</span>
        </div>
      </div>

      <!-- Show input wrapper always -->
      <div class="input-wrapper">
        <!-- Picture upload button -->
        <div
          class="picture-btn"
          @click="toggleImageInput"
          title="Add base64 image"
        >
          <svg
            class="picture-icon"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M21 19V5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19ZM8.5 13.5L11 16.51L14.5 12L19 18H5L8.5 13.5Z"
              fill="currentColor"
            />
          </svg>
        </div>

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
import BouncingDots from "./BouncingDots.vue";

export default {
  name: "HomePage",
  components: {
    LoadingDots,
    BouncingDots,
  },
  data() {
    return {
      userQuestion: "",
      selectedImage: null,
      imagePreviewUrl: null,
      imageBase64: null,
      apiResponse: null,
      isLoading: false,
      isEnergized: false,
      resizeObserver: null,
      showImageInput: false,
      base64Input: "",
      base64ContainerStyle: {
        top: "-165px",
      },
      chatMessages: [],
    };
  },
  watch: {
    showImageInput(newVal) {
      if (newVal) {
        // When showing the input, recalculate position after DOM update
        this.$nextTick(() => {
          this.calculateBase64Position();
        });
      }
    },
    apiResponse() {
      // Recalculate position when response changes layout
      if (this.showImageInput) {
        this.$nextTick(() => {
          this.calculateBase64Position();
        });
      }
    },
  },
  mounted() {
    this.setupResizeObserver();
    this.setupDynamicPositioning();
  },
  beforeUnmount() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    // Clean up window resize listener
    if (this.debouncedCalculatePosition) {
      window.removeEventListener("resize", this.debouncedCalculatePosition);
    }
  },
  methods: {
    triggerImageUpload() {
      this.$refs.imageInput.click();
    },

    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        // Validate file type
        if (!file.type.startsWith("image/")) {
          alert("Please select a valid image file");
          return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
          alert("Image size must be less than 10MB");
          return;
        }

        this.selectedImage = file;

        // Create preview URL
        this.imagePreviewUrl = URL.createObjectURL(file);

        // Convert to base64
        this.convertToBase64(file);

        console.log("Image selected:", file.name);
      }
    },

    convertToBase64(file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        // Get base64 string without the data:image/...;base64, prefix
        this.imageBase64 = e.target.result.split(",")[1];
        console.log("Base64 encoded, length:", this.imageBase64.length);
      };
      reader.readAsDataURL(file);
    },

    removeImage() {
      // Clean up preview URL
      if (this.imagePreviewUrl) {
        URL.revokeObjectURL(this.imagePreviewUrl);
      }

      this.selectedImage = null;
      this.imagePreviewUrl = null;
      this.imageBase64 = null;

      // Reset file input
      if (this.$refs.imageInput) {
        this.$refs.imageInput.value = "";
      }

      console.log("Image removed");
    },

    // Base64 input methods
    toggleImageInput() {
      this.showImageInput = !this.showImageInput;
      if (!this.showImageInput) {
        this.base64Input = "";
      }
      // Position calculation is now handled by the watcher
    },

    closeImageInput() {
      this.showImageInput = false;
      this.base64Input = "";
    },

    clearBase64() {
      this.base64Input = "";
    },

    getBase64Status() {
      if (!this.base64Input) return "";

      const length = this.base64Input.length;
      if (length < 100) return "Too short";
      if (this.isValidBase64(this.base64Input)) {
        return `Valid base64 (${Math.round(length / 1024)}KB)`;
      }
      return "Invalid base64";
    },

    isValidBase64(str) {
      try {
        // Check if string is valid base64
        const base64Regex = /^[A-Za-z0-9+/]*={0,2}$/;
        return base64Regex.test(str) && str.length % 4 === 0;
      } catch (e) {
        return false;
      }
    },

    async submitQuestion() {
      if (this.isLoading) return;

      // Don't submit if no question and no image
      if (!this.userQuestion.trim() && !this.base64Input.trim()) return;

      // Add user message to chat
      const userMessage = {
        type: "user",
        text: this.userQuestion || "Image uploaded",
        image:
          this.base64Input && this.isValidBase64(this.base64Input)
            ? this.base64Input
            : null,
        timestamp: new Date(),
      };
      this.chatMessages.push(userMessage);

      // Scroll to bottom after adding user message
      this.$nextTick(() => {
        this.scrollToBottom();
      });

      // Store the question and image for API call
      const questionText = this.userQuestion;
      const imageData =
        this.base64Input && this.isValidBase64(this.base64Input)
          ? this.base64Input
          : null;

      // Clear the input and base64 input immediately
      this.userQuestion = "";
      this.base64Input = "";
      this.showImageInput = false;

      // Start loading animation
      this.isLoading = true;

      // Add loading message to chat
      const loadingMessage = {
        type: "ai",
        isLoading: true,
        timestamp: new Date(),
      };
      this.chatMessages.push(loadingMessage);

      // Scroll to bottom after adding loading message
      this.$nextTick(() => {
        this.scrollToBottom();
      });

      console.log("Question submitted:", questionText || "Image uploaded");

      // Prepare the API payload
      const payload = {
        question: questionText,
      };

      // Add base64 image if available
      if (imageData) {
        payload.image = imageData;
        console.log("Base64 image attached (length):", imageData.length);
      }

      console.log("API Payload:", payload);

      try {
        // Send question and image to backend API
        const response = await fetch("/api/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(
            `API error: ${response.status} ${response.statusText}`
          );
        }

        const result = await response.json();
        console.log("API Response:", result);

        // Remove loading message and add AI response
        const loadingMessageIndex = this.chatMessages.findIndex(
          (msg) => msg.isLoading
        );
        if (loadingMessageIndex !== -1) {
          this.chatMessages.splice(loadingMessageIndex, 1);
        }

        // Add AI response to chat
        const aiMessage = {
          type: "ai",
          answer: result.answer,
          links: result.links || [],
          timestamp: new Date(),
        };
        this.chatMessages.push(aiMessage);

        // Scroll to bottom of chat with a slight delay to ensure content is rendered
        this.$nextTick(() => {
          setTimeout(() => {
            this.scrollToBottom();
          }, 100);
        });
      } catch (error) {
        console.error("Error submitting question:", error);

        // Remove loading message and add error message
        const loadingMessageIndex = this.chatMessages.findIndex(
          (msg) => msg.isLoading
        );
        if (loadingMessageIndex !== -1) {
          this.chatMessages.splice(loadingMessageIndex, 1);
        }

        // Add error message to chat
        const errorMessage = {
          type: "ai",
          answer:
            "Sorry, I encountered an error while processing your request. Please try again.",
          links: [],
          timestamp: new Date(),
        };
        this.chatMessages.push(errorMessage);

        // Scroll to bottom after error message
        this.$nextTick(() => {
          setTimeout(() => {
            this.scrollToBottom();
          }, 100);
        });
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

    scrollToBottom() {
      const chatMessages = this.$refs.chatMessages;
      if (chatMessages) {
        // Use requestAnimationFrame to ensure DOM is fully updated
        requestAnimationFrame(() => {
          chatMessages.scrollTop = chatMessages.scrollHeight;
        });
      }
    },

    setupResizeObserver() {
      if (typeof ResizeObserver !== "undefined") {
        this.resizeObserver = new ResizeObserver(() => {
          // Observer for future use if needed
        });

        const container = this.$el?.querySelector(".atom-container");
        if (container) {
          this.resizeObserver.observe(container);
        }
      }
    },

    // Dynamic positioning for base64 input container
    setupDynamicPositioning() {
      // Create debounced version of position calculation
      this.debouncedCalculatePosition = this.debounce(
        this.calculateBase64Position,
        100
      );

      // Set up resize listener for window
      window.addEventListener("resize", this.debouncedCalculatePosition);

      // Initial calculation
      this.calculateBase64Position();
    },

    debounce(func, wait) {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    },

    calculateBase64Position() {
      this.$nextTick(() => {
        const inputWrapper = this.$el?.querySelector(".input-wrapper");
        if (inputWrapper) {
          let containerHeight = this.getBase64ContainerHeight();

          // Try to get actual height if container exists (more precise)
          const existingContainer = this.$el?.querySelector(
            ".base64-input-container"
          );
          if (existingContainer) {
            const rect = existingContainer.getBoundingClientRect();
            if (rect.height > 0) {
              containerHeight = rect.height;
            }
          }

          const topPosition = -(containerHeight + 10); // 10px gap

          this.base64ContainerStyle = {
            top: `${topPosition}px`,
          };

          console.log(
            `Dynamic positioning: Container height ${containerHeight}px, positioned at ${topPosition}px`
          );
        }
      });
    },

    getBase64ContainerHeight() {
      // Try to create a temporary element to measure actual height
      try {
        const tempContainer = document.createElement("div");
        tempContainer.className = "base64-input-container";
        tempContainer.style.visibility = "hidden";
        tempContainer.style.position = "absolute";
        tempContainer.style.top = "-9999px";

        const header = document.createElement("div");
        header.className = "base64-input-header";
        header.innerHTML =
          '<span class="base64-label">Paste Base64 Image:</span>';

        const input = document.createElement("input");
        input.className = "base64-input";

        const actions = document.createElement("div");
        actions.className = "base64-input-actions";
        actions.innerHTML = '<button class="clear-base64-btn">Clear</button>';

        tempContainer.appendChild(header);
        tempContainer.appendChild(input);
        tempContainer.appendChild(actions);

        document.body.appendChild(tempContainer);
        const height = tempContainer.offsetHeight;
        document.body.removeChild(tempContainer);

        if (height > 0) {
          return height;
        }
      } catch (e) {
        console.log("Could not measure container height, using estimation");
      }

      // Fallback to viewport-based estimation
      const viewportWidth = window.innerWidth;

      if (viewportWidth <= 480) {
        return 110; // Mobile height estimation
      } else if (viewportWidth <= 768) {
        return 125; // Tablet height estimation
      } else if (viewportWidth <= 1024) {
        return 140; // Desktop small height estimation
      } else {
        return 155; // Desktop large height estimation
      }
    },
  },
};
</script>

<style scoped>
.home-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
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
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  pointer-events: auto;
}

/* Atom container */
.atom-container {
  position: relative;
  width: 400px;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 1000px;
  transform-style: preserve-3d;
}

/* Sine Curve Styles */
.sine-curve-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.sine-curve-svg {
  width: 400px;
  height: 400px;
  filter: drop-shadow(0 0 30px rgba(220, 20, 60, 0.4))
    drop-shadow(0 0 60px rgba(255, 69, 0, 0.3));
  transition: all 0.4s ease;
}

.atom-container.energized .sine-curve-svg {
  filter: drop-shadow(0 0 40px rgba(220, 20, 60, 0.7))
    drop-shadow(0 0 80px rgba(255, 69, 0, 0.5))
    drop-shadow(0 0 120px rgba(255, 20, 147, 0.4));
  transform: scale(1.05);
}

.sine-curve {
  stroke-dasharray: 1200;
  stroke-dashoffset: 0;
  animation: sineFlow 4s ease-in-out infinite;
}

.sine-glow {
  opacity: 0.6;
  animation: sineGlow 3s ease-in-out infinite;
}

.atom-container.energized .sine-glow {
  opacity: 1;
  animation: energizedSineGlow 1.5s ease-in-out infinite;
}

.sine-dot {
  filter: drop-shadow(0 0 4px rgba(220, 20, 60, 0.8));
}

.atom-container.energized .sine-dot {
  filter: drop-shadow(0 0 8px rgba(220, 20, 60, 1))
    drop-shadow(0 0 16px rgba(255, 69, 0, 0.8));
}

/* Sine curve animations */
@keyframes sineFlow {
  0%,
  100% {
    stroke-dashoffset: 0;
    opacity: 0.8;
  }
  50% {
    stroke-dashoffset: 100;
    opacity: 1;
  }
}

@keyframes sineGlow {
  0%,
  100% {
    stroke-width: 12;
    opacity: 0.4;
  }
  50% {
    stroke-width: 18;
    opacity: 0.8;
  }
}

@keyframes energizedSineGlow {
  0%,
  100% {
    stroke-width: 12;
    opacity: 0.6;
  }
  50% {
    stroke-width: 24;
    opacity: 1;
  }
}

/* Chat Container Styles */
.chat-container {
  width: 100%;
  max-width: 800px;
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-top: 140px;
  margin-bottom: 20px;
  min-height: 0;
  overflow: hidden;
  z-index: 2;
}

.chat-container.full-height {
  margin-top: 120px; /* Space for logo */
  margin-bottom: 20px;
  flex: 1;
  height: calc(
    100vh - 220px
  ); /* Full height minus top padding, logo space, and input area */
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px;
  scroll-behavior: smooth;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* Internet Explorer 10+ */
}

.chat-messages::-webkit-scrollbar {
  display: none; /* WebKit */
}

.message-wrapper {
  display: flex;
  margin-bottom: 16px;
  animation: messageSlideIn 0.3s ease-out;
}

.message-wrapper.user-message {
  justify-content: flex-end;
}

.message-wrapper.ai-message {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(220, 20, 60, 0.15);
  border-radius: 16px;
  padding: 12px 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 1px 0 rgba(255, 69, 0, 0.1) inset;
  position: relative;
}

.user-message .message-bubble {
  background: rgba(220, 20, 60, 0.15);
  border-color: rgba(220, 20, 60, 0.25);
  border-radius: 16px 16px 4px 16px;
}

.ai-message .message-bubble {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  border-radius: 16px 16px 16px 4px;
}

.message-text {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
  font-size: 14px;
  margin: 0;
  word-wrap: break-word;
}

.message-loading {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 4px 0;
  opacity: 0.8;
}

.message-image-container {
  margin-bottom: 12px;
}

.image-label {
  color: rgba(220, 20, 60, 0.9);
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 8px;
  display: block;
}

.message-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.message-links {
  margin-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 12px;
  animation: linksSlideIn 0.4s ease-out 0.1s both;
}

.links-header {
  color: rgba(220, 20, 60, 0.9);
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.links-header::before {
  content: "";
  width: 3px;
  height: 12px;
  background: linear-gradient(135deg, #dc143c, #ff4500);
  border-radius: 2px;
  animation: headerPulse 2s ease-in-out infinite;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-link-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.85);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  min-height: 44px;
}

.message-link-item::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(220, 20, 60, 0.1),
    transparent
  );
  transition: left 0.6s ease;
}

.message-link-item:hover::before {
  left: 100%;
}

.message-link-item:hover {
  background: rgba(220, 20, 60, 0.08);
  border-color: rgba(220, 20, 60, 0.25);
  color: rgba(255, 255, 255, 0.98);
  transform: translateX(3px) scale(1.02);
  box-shadow: 0 4px 12px rgba(220, 20, 60, 0.15),
    0 0 20px rgba(220, 20, 60, 0.05);
}

.message-link-item:active {
  transform: translateX(1px) scale(0.98);
}

.message-link-item .link-icon {
  width: 14px;
  height: 14px;
  color: rgba(220, 20, 60, 0.8);
  flex-shrink: 0;
  transition: all 0.3s ease;
  margin-top: 2px;
}

.message-link-item:hover .link-icon {
  color: rgba(220, 20, 60, 1);
  transform: rotate(5deg) scale(1.1);
}

.message-link-item:hover .link-title {
  color: rgba(255, 255, 255, 1);
}

.message-link-item:hover .link-url {
  color: rgba(220, 20, 60, 0.8);
}

.message-link-item .link-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.message-link-item .link-title {
  font-weight: 500;
  font-size: 12px;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: rgba(255, 255, 255, 0.9);
}

.message-link-item .link-url {
  font-size: 10px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.6);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: "Courier New", monospace;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes linksSlideIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes headerPulse {
  0%,
  100% {
    opacity: 0.8;
    transform: scaleY(1);
  }
  50% {
    opacity: 1;
    transform: scaleY(1.2);
  }
}

.input-container {
  position: relative;
  width: 100%;
  max-width: 800px;
  flex-shrink: 0;
  z-index: 3;
  margin-top: auto;
}

.image-preview-container {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(220, 20, 60, 0.15);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 1px 0 rgba(255, 69, 0, 0.1) inset,
    0 0 20px rgba(220, 20, 60, 0.05);
  animation: slideDown 0.3s ease-out;
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

.picture-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 8px;
  flex-shrink: 0;
  margin-right: 8px;
}

.picture-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.picture-icon {
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.8);
  transition: color 0.2s ease;
}

.picture-btn:hover .picture-icon {
  color: rgba(220, 20, 60, 0.9);
}

.hidden-file-input {
  display: none;
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

/* Base64 Input Container Styles */
.base64-input-container {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(220, 20, 60, 0.15);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 1px 0 rgba(255, 69, 0, 0.1) inset,
    0 0 20px rgba(220, 20, 60, 0.05);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.base64-input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.base64-label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.close-input-btn {
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-input-btn:hover {
  background: rgba(220, 20, 60, 0.2);
}

.close-icon {
  width: 16px;
  height: 16px;
  color: rgba(255, 255, 255, 0.7);
  transition: color 0.2s ease;
}

.close-input-btn:hover .close-icon {
  color: rgba(220, 20, 60, 0.9);
}

.base64-input {
  width: 100%;
  height: 45px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-family: "Courier New", monospace;
  font-size: 12px;
  outline: none;
  transition: all 0.3s ease;
}

.base64-input:focus {
  border-color: rgba(220, 20, 60, 0.3);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 2px rgba(220, 20, 60, 0.1);
}

.base64-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.base64-input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.clear-base64-btn {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-base64-btn:hover {
  background: rgba(220, 20, 60, 0.1);
  border-color: rgba(220, 20, 60, 0.3);
  color: rgba(220, 20, 60, 0.9);
}

.base64-status {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .home-container {
    padding: 32px 16px 32px 16px;
    height: 100vh;
  }

  .chat-container {
    margin-top: 100px;
    max-width: 650px;
  }

  .chat-container.full-height {
    margin-top: 80px;
    height: calc(100vh - 180px);
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
    width: 300px;
    height: 300px;
  }

  .sine-curve-svg {
    width: 300px;
    height: 300px;
  }

  .input-container {
    max-width: 650px;
  }

  .chat-container {
    max-width: 650px;
  }

  .chat-container.full-height {
    margin-top: 80px;
    height: calc(100vh - 180px);
  }

  .message-bubble {
    max-width: 85%;
    padding: 10px 14px;
  }

  .message-text {
    font-size: 13px;
  }

  .message-image {
    max-height: 150px;
  }

  .message-link-item {
    font-size: 11px;
    padding: 8px 10px;
    min-height: 40px;
  }

  .message-link-item .link-title {
    font-size: 11px;
  }

  .message-link-item .link-url {
    font-size: 9px;
  }

  .image-preview-container {
    padding: 10px;
    margin-bottom: 10px;
  }

  .preview-image {
    width: 50px;
    height: 50px;
  }

  .image-name {
    font-size: 13px;
    max-width: 150px;
  }

  .input-wrapper {
    padding: 5px;
    height: 52px;
  }

  .question-input {
    padding: 12px 16px;
    font-size: 15px;
  }

  .picture-btn {
    width: 42px;
    height: 42px;
    margin-right: 6px;
  }

  .picture-icon {
    width: 18px;
    height: 18px;
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

  .base64-input-container {
    padding: 14px;
  }

  .base64-input {
    font-size: 11px;
    padding: 10px;
    height: 40px;
  }
}

@media (max-width: 768px) {
  .home-container {
    padding: 24px 12px 24px 12px;
    height: 100vh;
  }

  .chat-container {
    margin-top: 100px;
    max-width: 100%;
  }

  .chat-container.full-height {
    margin-top: 70px;
    height: calc(100vh - 160px);
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
    width: 250px;
    height: 250px;
  }

  .sine-curve-svg {
    width: 250px;
    height: 250px;
  }

  .input-container {
    max-width: 100%;
  }

  .chat-container {
    max-width: 100%;
    margin: 16px 0;
  }

  .message-bubble {
    max-width: 90%;
    padding: 8px 12px;
  }

  .message-text {
    font-size: 12px;
  }

  .message-image {
    max-height: 120px;
  }

  .message-link-item {
    font-size: 10px;
    padding: 6px 8px;
    min-height: 38px;
  }

  .message-link-item .link-title {
    font-size: 10px;
  }

  .message-link-item .link-url {
    font-size: 8px;
  }

  .image-label {
    font-size: 11px;
  }

  .image-preview-container {
    padding: 8px;
    margin-bottom: 8px;
  }

  .preview-image {
    width: 45px;
    height: 45px;
  }

  .image-name {
    font-size: 12px;
    max-width: 120px;
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

  .picture-btn {
    width: 40px;
    height: 40px;
    margin-right: 5px;
  }

  .picture-icon {
    width: 16px;
    height: 16px;
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

  .base64-input-container {
    padding: 12px;
  }

  .base64-label {
    font-size: 13px;
  }

  .base64-input {
    font-size: 10px;
    padding: 8px;
    height: 35px;
  }

  .clear-base64-btn {
    padding: 5px 10px;
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .home-container {
    padding: 20px 8px 20px 8px;
    height: 100vh;
  }

  .chat-container {
    margin-top: 90px;
  }

  .chat-container.full-height {
    margin-top: 60px;
    height: calc(100vh - 140px);
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
    width: 220px;
    height: 220px;
  }

  .sine-curve-svg {
    width: 220px;
    height: 220px;
  }

  .response-container {
    padding: 8px;
    margin-bottom: 8px;
  }

  .chat-container {
    margin: 12px 0;
  }

  .message-wrapper {
    margin-bottom: 12px;
  }

  .message-bubble {
    max-width: 95%;
    padding: 6px 10px;
  }

  .message-text {
    font-size: 11px;
  }

  .message-image {
    max-height: 100px;
  }

  .message-link-item {
    font-size: 9px;
    padding: 5px 6px;
    min-height: 36px;
  }

  .message-link-item .link-title {
    font-size: 9px;
  }

  .message-link-item .link-url {
    font-size: 7px;
  }

  .image-label {
    font-size: 10px;
    margin-bottom: 6px;
  }

  .links-header {
    font-size: 10px;
  }

  .image-preview-container {
    padding: 6px;
    margin-bottom: 6px;
  }

  .image-preview-content {
    gap: 8px;
  }

  .preview-image {
    width: 40px;
    height: 40px;
  }

  .image-name {
    font-size: 11px;
    max-width: 100px;
  }

  .image-size,
  .base64-info {
    font-size: 10px;
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

  .picture-btn {
    width: 38px;
    height: 38px;
    margin-right: 4px;
  }

  .picture-icon {
    width: 15px;
    height: 15px;
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
    height: 100vh;
  }

  .chat-container {
    margin-top: 80px;
  }

  .chat-container.full-height {
    margin-top: 50px;
    height: calc(100vh - 120px);
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
    width: 180px;
    height: 180px;
  }

  .sine-curve-svg {
    width: 180px;
    height: 180px;
  }

  .response-container {
    padding: 6px;
    margin-bottom: 6px;
  }

  .chat-container {
    margin: 10px 0;
  }

  .message-wrapper {
    margin-bottom: 10px;
  }

  .message-bubble {
    max-width: 98%;
    padding: 5px 8px;
  }

  .message-text {
    font-size: 10px;
  }

  .message-image {
    max-height: 80px;
  }

  .message-link-item {
    font-size: 8px;
    padding: 4px 5px;
    min-height: 34px;
  }

  .message-link-item .link-title {
    font-size: 8px;
  }

  .message-link-item .link-url {
    font-size: 6px;
  }

  .image-label {
    font-size: 9px;
    margin-bottom: 4px;
  }

  .links-header {
    font-size: 9px;
  }

  .image-preview-container {
    padding: 5px;
    margin-bottom: 5px;
  }

  .image-preview-content {
    gap: 6px;
  }

  .preview-image {
    width: 35px;
    height: 35px;
  }

  .image-name {
    font-size: 10px;
    max-width: 80px;
  }

  .image-size,
  .base64-info {
    font-size: 9px;
  }

  .input-wrapper {
    padding: 3px;
    height: 40px;
  }

  .question-input {
    padding: 6px 10px;
    font-size: 13px;
  }

  .picture-btn {
    width: 34px;
    height: 34px;
    margin-right: 3px;
  }

  .picture-icon {
    width: 14px;
    height: 14px;
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

  .base64-input-container {
    padding: 8px;
  }

  .base64-label {
    font-size: 12px;
  }

  .base64-input {
    font-size: 9px;
    padding: 6px;
    height: 32px;
  }

  .clear-base64-btn {
    padding: 4px 8px;
    font-size: 10px;
  }

  .base64-status {
    font-size: 9px;
  }
}

/* Large screens */
@media (min-width: 1200px) {
  .home-container {
    padding: 48px 24px 48px 24px;
    height: 100vh;
  }

  .chat-container {
    margin-top: 160px;
    max-width: 900px;
  }

  .chat-container.full-height {
    margin-top: 140px;
    height: calc(100vh - 260px);
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
    width: 450px;
    height: 450px;
  }

  .sine-curve-svg {
    width: 450px;
    height: 450px;
  }

  .input-container {
    max-width: 900px;
  }

  .chat-container {
    max-width: 900px;
  }

  .message-bubble {
    max-width: 65%;
    padding: 16px 20px;
  }

  .message-text {
    font-size: 15px;
  }

  .message-image {
    max-height: 250px;
  }

  .message-link-item {
    font-size: 13px;
    padding: 10px 12px;
    min-height: 46px;
  }

  .message-link-item .link-title {
    font-size: 13px;
  }

  .message-link-item .link-url {
    font-size: 11px;
  }

  .image-label {
    font-size: 13px;
  }

  .links-header {
    font-size: 13px;
  }

  .image-preview-container {
    padding: 16px;
    margin-bottom: 16px;
  }

  .preview-image {
    width: 70px;
    height: 70px;
  }

  .image-name {
    font-size: 15px;
    max-width: 250px;
  }

  .image-size {
    font-size: 13px;
  }

  .base64-info {
    font-size: 12px;
  }

  .input-wrapper {
    padding: 8px;
    height: 60px;
  }

  .question-input {
    padding: 16px 20px;
    font-size: 16px;
  }

  .picture-btn {
    width: 48px;
    height: 48px;
    margin-right: 10px;
  }

  .picture-icon {
    width: 22px;
    height: 22px;
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
