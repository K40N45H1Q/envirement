import router from './router'
import { createApp } from 'vue'
import Bootstrap from './Bootstrap.vue'
import '@fortawesome/fontawesome-free/css/all.css';

createApp(Bootstrap).use(router).mount('#root')
