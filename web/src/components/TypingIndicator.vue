<template>
  <div class="typing msg">
    <span class="dots" aria-hidden="true"><i /><i /><i /></span>
  </div>
</template>

<style scoped>
.typing {
  animation: typing-in 0.25s ease both;
  padding: 4px 2px;
}
@keyframes typing-in {
  from {
    opacity: 0;
  }
}

.dots {
  display: inline-flex;
  gap: 5px;
}
.dots i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #6a6a6a;
  animation: bounce 1.2s ease-in-out infinite;
}
.dots i:nth-child(2) {
  animation-delay: 0.15s;
}
.dots i:nth-child(3) {
  animation-delay: 0.3s;
}
@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.35;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}
</style>
