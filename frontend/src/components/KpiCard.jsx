import { motion } from 'framer-motion';

export default function KpiCard({ title, value, accent = 'cyan', subtitle }) {
  const accentClass = accent === 'danger' ? 'text-danger border-danger/40 shadow-danger' : accent === 'warning' ? 'text-warning border-warning/40' : 'text-cyan border-cyan/40 shadow-neon';

  return (
    <motion.div whileHover={{ y: -4 }} className={`glass-card p-4 border ${accentClass}`}>
      <p className="text-sm text-white/70">{title}</p>
      <h3 className="font-display text-3xl mt-2">{value}</h3>
      {subtitle && <p className="text-sm mt-1 text-white/70">{subtitle}</p>}
    </motion.div>
  );
}
