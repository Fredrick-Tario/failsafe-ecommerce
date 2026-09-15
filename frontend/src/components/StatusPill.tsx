import type { SystemState } from '../types'
 
interface StatusPillProps {
  state: SystemState
}
 
const labels: Record<SystemState, string> = {
  checking: 'Checking systems',
  operational: 'All systems operational',
  degraded: 'Service degradation detected',
}
 
export default function StatusPill({ state }: StatusPillProps) {
  return (
    <div className={`status-pill status-${state}`}>
      <span className="status-dot" aria-hidden="true" />
      <span>{labels[state]}</span>
    </div>
  )
}
