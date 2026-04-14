---
paths: ["src/components/**", "app/components/**", "src/pages/**", "app/pages/**"]
---
<!-- astra:managed -->
- Use existing components from the project's component library before creating new ones.
- Follow the project's CSS approach (Tailwind/CSS modules/styled-components).
- All new components must be responsive (mobile-first) and keyboard accessible.
- Reference design tokens from the theme file, never use raw hex/px values.
- Every interactive element needs ARIA attributes and visible focus states.
- Touch targets minimum 44x44px on mobile.
