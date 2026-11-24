import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, radius, space, type } from '@/components/theme';
import { Button, ErrorText, Loading, Screen, Subtitle } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import type { TestQuestions } from '@/lib/types';

type Choice = 'a' | 'b';

/** Taking a test: one pair of statements at a time, choose the one closer to you. */
export default function TakeTestScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [test, setTest] = useState<TestQuestions | null>(null);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, Choice>>({});
  const [error, setError] = useState('');
  const [sending, setSending] = useState(false);
  const advance = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    api<TestQuestions>(`/tests/${id}`).then(setTest).catch((e) => setError(errorMessage(e)));
    return () => {
      if (advance.current) clearTimeout(advance.current);
    };
  }, [id]);

  if (!test) {
    return <Screen topInset={false}>{error ? <ErrorText>{error}</ErrorText> : <Loading />}</Screen>;
  }

  const total = test.questions.length;
  const question = test.questions[index];
  const allAnswered = Object.keys(answers).length === total;
  const isLast = index === total - 1;

  function choose(choice: Choice) {
    setAnswers((a) => ({ ...a, [question.id]: choice }));
    // A short pause so the choice is visible before the next pair appears.
    if (advance.current) clearTimeout(advance.current);
    if (!isLast) advance.current = setTimeout(() => setIndex((i) => Math.min(i + 1, total - 1)), 250);
  }

  async function submit() {
    setSending(true);
    try {
      await api(`/tests/${test!.id}`, { method: 'POST', json: { answers } });
      router.replace({ pathname: '/test-result', params: { test: test!.id, whose: 'me' } });
    } catch (e) {
      setError(errorMessage(e));
      setSending(false);
    }
  }

  return (
    <Screen topInset={false}>
      <Stack.Screen options={{ title: test.title }} />

      <View style={{ gap: 8 }}>
        <Text style={[type.captionStrong, { color: colors.muted }]}>
          {index + 1} из {total}
        </Text>
        <View style={styles.bar}>
          <View style={[styles.barFill, { width: `${((index + 1) / total) * 100}%` }]} />
        </View>
      </View>

      <Text style={[type.titleS, { color: colors.text, marginTop: space.sm }]}>{test.prompt}</Text>
      <Subtitle>Выберите то, что ближе. Если подходят оба — что важнее.</Subtitle>

      {(['a', 'b'] as const).map((side) => {
        const selected = answers[question.id] === side;
        return (
          <Pressable
            key={side}
            accessibilityRole="button"
            accessibilityState={{ selected }}
            onPress={() => choose(side)}
            style={({ pressed }) => [
              styles.option,
              pressed && !selected && { backgroundColor: colors.surface },
              selected && styles.optionSelected,
            ]}>
            <View style={[styles.letter, selected && styles.letterSelected]}>
              <Text style={[type.captionStrong, { color: selected ? colors.text : colors.muted }]}>
                {side === 'a' ? 'А' : 'Б'}
              </Text>
            </View>
            <Text style={[type.subheading, { flex: 1, color: selected ? '#fff' : colors.text }]}>
              {question[side]}
            </Text>
          </Pressable>
        );
      })}

      <View style={styles.nav}>
        <Button
          title="Назад"
          variant="text"
          size="small"
          icon="arrow-back-outline"
          disabled={index === 0}
          onPress={() => setIndex(index - 1)}
        />
        {!isLast && answers[question.id] ? (
          <Button title="Дальше" variant="text" size="small" onPress={() => setIndex(index + 1)} />
        ) : null}
      </View>

      {allAnswered ? <Button title="Узнать результат" onPress={submit} loading={sending} /> : null}
      <ErrorText>{error}</ErrorText>
    </Screen>
  );
}

const styles = StyleSheet.create({
  bar: { height: 4, backgroundColor: colors.surface, borderRadius: 2, overflow: 'hidden' },
  barFill: { height: 4, backgroundColor: colors.black },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: space.md,
    minHeight: 96,
    padding: 20,
    borderRadius: radius.xl,
    borderWidth: 1.5,
    borderColor: colors.border,
    backgroundColor: colors.background,
  },
  optionSelected: { backgroundColor: colors.black, borderColor: colors.black },
  letter: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  letterSelected: { backgroundColor: '#fff' },
  nav: { flexDirection: 'row', justifyContent: 'space-between' },
});
