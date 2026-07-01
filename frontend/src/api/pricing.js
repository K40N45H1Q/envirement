import { apiRequest } from '@/api/client'

export const getPricingPlans = (billingPeriod = 'monthly') => apiRequest(
  `/api/pricing/plans?billing_period=${encodeURIComponent(billingPeriod)}`,
  { skipAuth: true },
)
