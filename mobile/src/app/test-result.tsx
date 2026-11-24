import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { usePartner } from '@/auth/auth-context';
import { colors, space, type } from '@/components/theme';
import { Button, Card, Empty, ErrorText, Loading, Screen, SectionTitle, Subtitle } from '@/components/ui';
import { errorMessage } from '@/lib/api';
import { formatDate, localDay } from '@/lib/dates';
import { leadingTitles, loadResult } from '@/lib/tests';
import type { TestId, TestResult } from '@/lib/types';

const SUBJECT: Record<TestId, string> = { love: 'язык любви', apology: 'язык извинений' };

export default function TestResultScreen() {
  const { test, whose } = useLocalSearchParams<{ test: TestId; whose: 'me' | 'partner' }>();
  const partner = usePartner();
  const [result, setResult] = useState<TestResult | null | undefined>(undefined);
  const [error, setError] = useState('');
  const isPartner = whose === 'partner';

  useEffect(() => {
    loadResult(test, isPartner ? 'partner' : 'me')
      .then(setResult)
      .catch((e) => setError(errorMessage(e)));
  }, [test, isPartner]);

  if (error) return <Screen topInset={false}><ErrorText>{error}</ErrorText></Screen>;
  if (result === undefined) return <Screen topInset={false}><Loading /></Screen>;
  if (result === null) return <Screen topInset={false}><Empty>Тест ещё не пройден.</Empty></Screen>;

  const allEqual = result.leading.length === result.scores.length;
  const titles = leadingTitles(result);

  return (
    <Screen topInset={false}>
      <Stack.Screen options={{ title: result.title }} />
      <Subtitle>
        {isPartner ? `${partner?.profile.name ?? 'Партнёр'}: ${SUBJECT[test]}` : `Ваш ${SUBJECT[test]}`}
        {!allEqual && titles.length > 1 ? ' — их несколько' : ''}
      </Subtitle>
      <Text style={[type.title, { color: colors.text }]}>
        {allEqual ? 'Все одинаково важны' : titles.join(' и ')}
      </Text>

      <Card style={{ gap: 14 }}>
        {result.scores.map((s) => {
          const lead = result.leading.includes(s.key) && !allEqual;
          return (
            <View key={s.key} style={{ gap: 6 }}>
              <View style={styles.scoreRow}>
                <Text style={[lead ? type.bodyStrong : type.body, { color: colors.text, flex: 1 }]}>{s.title}</Text>
                <Text style={[type.caption, { color: colors.muted }]}>
                  {s.points} из {s.max}
                </Text>
              </View>
              <View style={styles.bar}>
                <View style={[styles.barFill, { width: `${s.percent}%` }, lead && { backgroundColor: colors.heart }]} />
              </View>
            </View>
          );
        })}
      </Card>

      {allEqual ? (
        <Subtitle>
          Ни один язык не выделился. Попробуйте пройти тест ещё раз и в каждой паре выбирать то, что
          действительно ближе.
        </Subtitle>
      ) : (
        <>
          <SectionTitle>{isPartner ? result.advice_title : 'Что это значит'}</SectionTitle>
          {result.advice.map((a) => (
            <Card key={a.key} style={{ gap: 6 }}>
              <Text style={[type.subheading, { color: colors.text }]}>{a.title}</Text>
              <Subtitle>{a.description}</Subtitle>
              <Text style={[type.body, { color: colors.text, marginTop: space.xs }]}>
                {isPartner ? a.advice : `Партнёру: ${a.advice.charAt(0).toLowerCase()}${a.advice.slice(1)}`}
              </Text>
            </Card>
          ))}
        </>
      )}

      <Subtitle>Пройден {formatDate(localDay(result.taken_at))}</Subtitle>
      {!isPartner ? (
        <Button
          title="Пройти заново"
          variant="secondary"
          icon="refresh-outline"
          onPress={() => router.replace({ pathname: '/test/[id]', params: { id: test } })}
        />
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  scoreRow: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
  bar: { height: 6, backgroundColor: colors.surface, borderRadius: 3, overflow: 'hidden' },
  barFill: { height: 6, backgroundColor: colors.black },
});
