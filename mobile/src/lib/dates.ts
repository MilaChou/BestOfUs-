/** Dates: the server uses "2000-05-14"; people type and read "14.05.2000" / "14 мая 2000". */

const MONTHS = [
  'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
];

export function todayIso(): string {
  return isoOf(new Date());
}

/** A Date -> "2026-11-15" in local time. */
export function isoOf(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

function pad(n: number): string {
  return String(n).padStart(2, '0');
}

/** "2000-05-14" -> "14 мая 2000". withYear=false -> "14 мая". */
export function formatDate(iso: string | null, withYear = true): string {
  if (!iso) return '';
  const [y, m, d] = iso.slice(0, 10).split('-').map(Number);
  return `${d} ${MONTHS[m - 1]}${withYear ? ` ${y}` : ''}`;
}

/** "2000-05-14" -> "14.05.2000" for an input field. */
export function isoToInput(iso: string | null): string {
  if (!iso) return '';
  const [y, m, d] = iso.slice(0, 10).split('-');
  return `${d}.${m}.${y}`;
}

/** "14.05.2000" -> "2000-05-14", or null if it's not a real date. */
export function inputToIso(text: string): string | null {
  const match = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(text.trim());
  if (!match) return null;
  const [, d, m, y] = match.map(Number);
  const date = new Date(y, m - 1, d);
  if (date.getFullYear() !== y || date.getMonth() !== m - 1 || date.getDate() !== d) return null;
  return `${y}-${pad(m)}-${pad(d)}`;
}

/** As the user types digits, add the dots: "1405" -> "14.05". */
export function maskDate(text: string): string {
  const digits = text.replace(/\D/g, '').slice(0, 8);
  const parts = [digits.slice(0, 2), digits.slice(2, 4), digits.slice(4, 8)].filter(Boolean);
  return parts.join('.');
}

/** "сегодня", "завтра", "вчера" or "14 мая". */
export function relativeDay(iso: string): string {
  const today = todayIso();
  const diff = Math.round((Date.parse(iso) - Date.parse(today)) / 86_400_000);
  if (diff === 0) return 'сегодня';
  if (diff === 1) return 'завтра';
  if (diff === -1) return 'вчера';
  const sameYear = iso.slice(0, 4) === today.slice(0, 4);
  return formatDate(iso, !sameYear);
}

/** Russian plural: plural(5, 'день', 'дня', 'дней') -> 'дней'. */
export function plural(n: number, one: string, few: string, many: string): string {
  if (n % 10 === 1 && n % 100 !== 11) return one;
  if (n % 10 >= 2 && n % 10 <= 4 && !(n % 100 >= 12 && n % 100 <= 14)) return few;
  return many;
}

export function formatPrice(price: number | null): string {
  if (price === null) return '';
  if (price === 0) return 'своими руками';
  return `${price.toLocaleString('ru-RU')} ₽`;
}

/**
 * A server timestamp -> the local calendar day "2026-11-15".
 * The server stores UTC; without the zone marker it's still UTC, so we add "Z".
 */
export function localDay(timestamp: string): string {
  const hasZone = /[zZ]|[+-]\d\d:?\d\d$/.test(timestamp);
  const d = new Date(hasZone ? timestamp : `${timestamp}Z`);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

/** Days from today until the next time this date's day-and-month comes (0 = today). */
export function daysUntilYearly(iso: string): number {
  const today = new Date(`${todayIso()}T00:00:00`);
  const [, m, d] = iso.slice(0, 10).split('-').map(Number);
  let next = new Date(today.getFullYear(), m - 1, d);
  if (next < today) next = new Date(today.getFullYear() + 1, m - 1, d);
  return Math.round((next.getTime() - today.getTime()) / 86_400_000);
}

export const MONTHS_NOMINATIVE = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
];

/** "через 6 дней", "завтра", "сегодня". */
export function inDays(n: number): string {
  if (n === 0) return 'сегодня';
  if (n === 1) return 'завтра';
  return `через ${n} ${plural(n, 'день', 'дня', 'дней')}`;
}
