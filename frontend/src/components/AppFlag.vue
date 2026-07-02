<script setup>
import { computed } from 'vue'

import beFlag from 'flag-icons/flags/4x3/be.svg'
import czFlag from 'flag-icons/flags/4x3/cz.svg'
import deFlag from 'flag-icons/flags/4x3/de.svg'
import eeFlag from 'flag-icons/flags/4x3/ee.svg'
import euFlag from 'flag-icons/flags/4x3/eu.svg'
import fiFlag from 'flag-icons/flags/4x3/fi.svg'
import frFlag from 'flag-icons/flags/4x3/fr.svg'
import lvFlag from 'flag-icons/flags/4x3/lv.svg'
import nlFlag from 'flag-icons/flags/4x3/nl.svg'
import plFlag from 'flag-icons/flags/4x3/pl.svg'

const props = defineProps({
  code: {
    type: String,
    required: true,
  },
  alt: {
    type: String,
    default: '',
  },
})

const flagMap = {
  be: beFlag,
  cz: czFlag,
  de: deFlag,
  ee: eeFlag,
  eu: euFlag,
  fi: fiFlag,
  fr: frFlag,
  lv: lvFlag,
  nl: nlFlag,
  pl: plFlag,
}

const src = computed(() => flagMap[String(props.code || '').trim().toLowerCase()] || euFlag)
</script>

<template>
  <img :src="src" :alt="alt" class="app-flag" loading="lazy" decoding="async" />
</template>

<style scoped>
.app-flag {
  width: 1.1rem;
  height: 0.85rem;
  display: inline-block;
  object-fit: cover;
  border-radius: 0.15rem;
  box-shadow: 0 0 0 0.0625rem rgba(21, 32, 27, 0.08);
  flex-shrink: 0;
  vertical-align: middle;
}
</style>
