<template>
  <div class="text-left px-4 py-2 flex items-center justify-center">
    <svg
      class="animate-spin h-5 w-5 mr-2 text-red-700"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      ></circle>
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 11-8 8z"
      ></path>
    </svg>
    <slot></slot>
  </div>
</template>
