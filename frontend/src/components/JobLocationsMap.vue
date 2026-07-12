<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  jobs: {
    type: Array,
    default: () => [],
  },
  selectedCountry: {
    type: String,
    default: 'all',
  },
  activeJobId: {
    type: [Number, String, null],
    default: null,
  },
  height: {
    type: String,
    default: '20rem',
  },
})

const emit = defineEmits(['select-job'])
const mapElement = ref(null)
let leafletMap = null
let leafletLayer = null
let leafletModule = null

const mapTileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const mapTileAttribution = '&copy; OpenStreetMap contributors'

const fallbackCoordinates = {
  germany: [52.52, 13.405],
  netherlands: [51.9244, 4.4777],
  poland: [52.2297, 21.0122],
  belgium: [51.2194, 4.4025],
  france: [48.8566, 2.3522],
  latvia: [56.9496, 24.1052],
  estonia: [59.437, 24.7536],
  other: [54.526, 15.2551],
}

const locationCoordinates = [
  { match: /(berlin|герман|germany)/i, coords: [52.52, 13.405] },
  { match: /(rotterdam|netherlands|нидер)/i, coords: [51.9244, 4.4777] },
  { match: /(warsaw|poland|польш)/i, coords: [52.2297, 21.0122] },
  { match: /(antwerp|belgium|бельг)/i, coords: [51.2194, 4.4025] },
  { match: /(paris|france|франц)/i, coords: [48.8566, 2.3522] },
  { match: /(riga|latvia|латв)/i, coords: [56.9496, 24.1052] },
  { match: /(tallinn|estonia|эстон)/i, coords: [59.437, 24.7536] },
]

const markerJobs = computed(() => props.jobs
  .map((job) => {
    const location = `${job.displayLocation || job.location || ''} ${job.countryLabel || ''}`
    const matched = locationCoordinates.find((item) => item.match.test(location))
    const coords = matched?.coords || fallbackCoordinates[job.countryKey] || fallbackCoordinates.other

    return {
      id: job.id,
      title: job.title,
      company: job.company,
      salary: job.salary,
      location: job.displayLocation || job.location,
      coords,
      color: job.id === props.activeJobId ? '#0f8a56' : '#1da86b',
    }
  }))

const renderMarkers = async () => {
  if (!leafletMap || !leafletModule) return

  if (leafletLayer) {
    leafletLayer.clearLayers()
  } else {
    leafletLayer = leafletModule.layerGroup().addTo(leafletMap)
  }

  const points = []

  markerJobs.value.forEach((job) => {
    if (!job.coords) return
    points.push(job.coords)

    const marker = leafletModule.circleMarker(job.coords, {
      radius: job.id === props.activeJobId ? 11 : 8,
      color: job.color,
      fillColor: job.color,
      fillOpacity: 0.85,
      weight: 2,
    })

    marker.bindPopup(`
      <div style="min-width: 170px;">
        <strong>${job.title}</strong><br/>
        <span>${job.company}</span><br/>
        <span>${job.location}</span><br/>
        <span>${job.salary}</span>
      </div>
    `)

    marker.on('click', () => emit('select-job', job.id))
    marker.addTo(leafletLayer)
  })

  if (!points.length) {
    leafletMap.setView(fallbackCoordinates.other, 4)
    return
  }

  if (points.length === 1) {
    leafletMap.setView(points[0], 5)
    return
  }

  leafletMap.fitBounds(points, { padding: [24, 24] })
}

onMounted(async () => {
  leafletModule = await import('leaflet')
  leafletMap = leafletModule.map(mapElement.value, {
    zoomControl: true,
    scrollWheelZoom: false,
  }).setView(fallbackCoordinates.other, 4)

  leafletMap.attributionControl.setPrefix('')

  leafletModule.tileLayer(mapTileUrl, {
    attribution: mapTileAttribution,
  }).addTo(leafletMap)

  await renderMarkers()
})

watch(markerJobs, renderMarkers, { deep: true })

onBeforeUnmount(() => {
  if (leafletMap) {
    leafletMap.remove()
    leafletMap = null
  }
})
</script>

<template>
  <div ref="mapElement" class="job-map" :style="{ height }"></div>
</template>

<style scoped>
.job-map {
  position: relative;
  z-index: 0;
  isolation: isolate;
  width: 100%;
  border-radius: 1rem;
  overflow: hidden;
  border: 0.0625rem solid var(--border-subtle);
  box-shadow: inset 0 0 0 0.0625rem rgba(29, 168, 107, 0.04);
}

.job-map :deep(.leaflet-popup-content-wrapper) {
  border-radius: 0.9rem;
}

.job-map :deep(.leaflet-control-zoom a) {
  color: var(--brand-strong);
}
</style>
