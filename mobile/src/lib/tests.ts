import { api, ApiError } from './api';
import type { TestId, TestResult } from './types';

/** A result, or null if the test hasn't been taken yet. */
export async function loadResult(test: TestId, whose: 'me' | 'partner'): Promise<TestResult | null> {
  try {
    return await api<TestResult>(`/tests/${test}/${whose}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

/** The leading category titles, e.g. ["Время вместе"]. */
export function leadingTitles(result: TestResult): string[] {
  return result.scores.filter((s) => result.leading.includes(s.key)).map((s) => s.title);
}

/** One line for lists: "Время вместе", or a note when everything came out equal. */
export function leadingLine(result: TestResult): string {
  if (result.leading.length === result.scores.length) return 'Все языки одинаково важны';
  return leadingTitles(result).join(', ');
}
