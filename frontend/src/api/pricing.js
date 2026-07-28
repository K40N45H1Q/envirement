import { apiRequest } from '@/api/client'

export const getPricingPlans = (billingPeriod = 'monthly') => apiRequest(
  `/api/pricing/plans?billing_period=${encodeURIComponent(billingPeriod)}`,
  { skipAuth: true },
)

export const createEmployerPlanCheckout = ({ planId, returnPath }) => apiRequest('/api/payments/checkout', {
  method: 'POST',
  body: JSON.stringify({
    plan_id: planId,
    return_path: returnPath,
  }),
})

export const confirmEmployerPlanCheckout = ({ sessionId }) => apiRequest('/api/payments/checkout/confirm', {
  method: 'POST',
  body: JSON.stringify({
    session_id: sessionId,
  }),
})
