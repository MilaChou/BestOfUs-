import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';

import { leadingLine, loadResult } from '@/lib/tests';
import type { TestId, TestResult } from '@/lib/types';

import { Card, type IconName, Row } from './ui';

const TESTS: { id: TestId; title: string; icon: IconName }[] = [
  { id: 'love', title: 'Язык любви', icon: 'heart-outline' },
  { id: 'apology', title: 'Язык извинений', icon: 'chatbubbles-outline' },
];

/** Both test results of me or my partner, as rows that open the result (or the test). */
export function TestRows({ whose }: { whose: 'me' | 'partner' }) {
  const [results, setResults] = useState<Partial<Record<TestId, TestResult | null>>>({});

  useFocusEffect(
    useCallback(() => {
      for (const t of TESTS) {
        loadResult(t.id, whose)
          .then((r) => setResults((all) => ({ ...all, [t.id]: r })))
          .catch(() => {});
      }
    }, [whose]),
  );

  return (
    <Card style={{ padding: 0 }}>
      {TESTS.map((t) => {
        const result = results[t.id];
        const taken = !!result;
        const open = () => router.push({ pathname: '/test-result', params: { test: t.id, whose } });
        const take = () => router.push({ pathname: '/test/[id]', params: { id: t.id } });
        return (
          <Row
            key={t.id}
            icon={t.icon}
            title={t.title}
            subtitle={
              taken
                ? leadingLine(result)
                : whose === 'me'
                  ? 'Пройти тест'
                  : 'Тест ещё не пройден'
            }
            onPress={taken ? open : whose === 'me' ? take : undefined}
          />
        );
      })}
    </Card>
  );
}
