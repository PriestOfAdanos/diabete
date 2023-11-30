import { defineConfig } from 'astro/config';
import preact from '@astrojs/preact';

export default defineConfig({
	// Enable Preact to support Preact JSX components.
	integrations: [preact()],
});

// https://astro.build/config
