import router from './router'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Bootstrap from './Bootstrap.vue'
import '@fortawesome/fontawesome-free/css/all.css';

const app = createApp(Bootstrap)

app.use(createPinia())
app.use(router)
app.mount('#root')
