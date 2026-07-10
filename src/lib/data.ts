import inbox from '../data/inbox.json';

export type Pillar = 'case' | 'theory' | 'memo' | 'data';
export type Tier = 'authority' | 'frontier' | 'frontier-x' | 'cn';
export type Signal = 'high' | 'medium' | 'low';

export interface Annotation {
  type: 'data' | 'decision' | 'insight';
  quote: string;
  note: string;
}

export interface InboxItem {
  id: string;
  feed: string;
  tier: Tier;
  pillar: Pillar;
  relevance_score: number;
  tags: string[];
  structured_summary: {
    background: string;
    decision_action: string;
    result: string;
    lesson: string;
  };
  executive_takeaway: string;
  signal_strength: Signal;
  title: string;
  link: string;
  published: string;
  ingested_at: string;
  content?: string | null;
  annotations?: Annotation[];
}

export const items: InboxItem[] = (inbox as { items: InboxItem[] }).items;

export const PILLAR_LABELS: Record<Pillar, string> = {
  case: '案例',
  theory: '理论',
  memo: '备忘录',
  data: '数据',
};

export const PILLAR_FULL: Record<Pillar, string> = {
  case: '实践案例',
  theory: '理论与框架',
  memo: '高管备忘录',
  data: '调研与数据',
};

export const TIER_LABELS: Record<Tier, string> = {
  authority: '权威',
  frontier: '前沿',
  'frontier-x': '前沿·X',
  cn: '中文',
};

export const SIGNAL_LABELS: Record<Signal, string> = {
  high: '高信号',
  medium: '中信号',
  low: '低信号',
};

export function sortByDate(list: InboxItem[]): InboxItem[] {
  return [...list].sort((a, b) => (a.published < b.published ? 1 : -1));
}

export function byPillar(pillar: Pillar): InboxItem[] {
  return sortByDate(items.filter(i => i.pillar === pillar));
}

// 按日期分组，key 形如 "2026-06-30"
export function groupByDate(list: InboxItem[]): { date: string; items: InboxItem[] }[] {
  const groups: Record<string, InboxItem[]> = {};
  for (const it of list) {
    const d = (it.published || '').slice(0, 10);
    (groups[d] = groups[d] || []).push(it);
  }
  return Object.entries(groups)
    .sort((a, b) => (a[0] < b[0] ? 1 : -1))
    .map(([date, items]) => ({ date, items }));
}

// 中文星期
export function weekdayLabel(dateStr: string): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return '';
  const w = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()];
  const m = dateStr.slice(5, 10).replace('-', '月');
  return `${m}日 ${w}`;
}

// 热点榜：signal_strength=high 优先，其次 medium，按 relevance_score 排
export function hotRanking(list: InboxItem[], n = 5): InboxItem[] {
  const weight: Record<Signal, number> = { high: 3, medium: 2, low: 1 };
  return [...list]
    .sort((a, b) => {
      const s = weight[b.signal_strength] - weight[a.signal_strength];
      if (s !== 0) return s;
      return b.relevance_score - a.relevance_score;
    })
    .slice(0, n);
}

export function relatedItems(item: InboxItem, n = 3): InboxItem[] {
  return sortByDate(
    items.filter(
      i => i.id !== item.id && (i.pillar === item.pillar || i.tags.some(t => item.tags.includes(t)))
    )
  ).slice(0, n);
}
