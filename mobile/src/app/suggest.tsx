import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { colors, space } from '@/components/theme';
import { Button, Card, Chip, ChipRow, ErrorText, Label, Screen, Subtitle } from '@/components/ui';
import { api, ApiError, errorMessage } from '@/lib/api';
import { BUDGETS, CUISINES, FORMATS, keysOf, TIMES } from '@/lib/labels';
import type { Budget, Cuisine, Format, Suggestion, TimeOfDay } from '@/lib/types';

/** Tap a selected chip again to clear it ("any"). */
function toggle<T>(current: T | null, value: T): T | null {
  return current === value ? null : value;
}

export default function SuggestScreen() {
  const [time, setTime] = useState<TimeOfDay | null>(null);
  const [format, setFormat] = useState<Format | null>(null);
  const [cuisine, setCuisine] = useState<Cuisine | null>(null);
  const [budget, setBudget] = useState<Budget | null>(null);

  const [suggestion, setSuggestion] = useState<Suggestion | null>(null);
  const [seenIdeas, setSeenIdeas] = useState<number[]>([]);
  const [seenCatalog, setSeenCatalog] = useState<string[]>([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  /** Changing a filter starts over: "ещё" only skips what was shown for these filters. */
  function changeFilter(apply: () => void) {
    apply();
    setSuggestion(null);
    setSeenIdeas([]);
    setSeenCatalog([]);
    setMessage('');
  }

  async function suggest(more: boolean) {
    setError('');
    setMessage('');
    setSaved(false);
    setLoading(true);
    const excludeIdeas = more ? seenIdeas : [];
    const excludeCatalog = more ? seenCatalog : [];
    try {
      const result = await api<Suggestion>('/couple/ideas/suggest', {
        query: {
          time_of_day: time,
          format,
          cuisine: format === 'food' ? cuisine : null,
          max_budget: budget,
          exclude_ideas: excludeIdeas,
          exclude_catalog: excludeCatalog,
        },
      });
      setSuggestion(result);
      if (result.source === 'idea') setSeenIdeas([...excludeIdeas, result.idea.id]);
      else setSeenCatalog([...excludeCatalog, result.activity.id]);
      if (!more) {
        if (result.source === 'idea') setSeenCatalog([]);
        else setSeenIdeas([]);
      }
    } catch (e) {
      setSuggestion(null);
      if (e instanceof ApiError && e.status === 404) {
        setMessage(
          more
            ? 'Варианты закончились. Попробуйте другие фильтры.'
            : 'Ничего не нашлось — попробуйте убрать часть фильтров.',
        );
      } else {
        setError(errorMessage(e));
      }
    } finally {
      setLoading(false);
    }
  }

  async function saveToIdeas() {
    if (suggestion?.source !== 'catalog') return;
    try {
      await api(`/couple/ideas/from-catalog/${suggestion.activity.id}`, { method: 'POST' });
      setSaved(true);
    } catch (e) {
      setError(errorMessage(e));
    }
  }

  const item = suggestion?.source === 'idea' ? suggestion.idea : suggestion?.activity;

  return (
    <Screen topInset={false}>
      <Subtitle>Не знаете, чем заняться? Выберите, что важно, — остальное оставьте «любым».</Subtitle>

      <Label>Время суток</Label>
      <ChipRow>
        {keysOf(TIMES).map((key) => (
          <Chip key={key} label={TIMES[key]} selected={time === key} onPress={() => changeFilter(() => setTime(toggle(time, key)))} />
        ))}
      </ChipRow>

      <Label>Чего хочется</Label>
      <ChipRow>
        {keysOf(FORMATS)
          .filter((key) => key !== 'other')
          .map((key) => (
            <Chip
              key={key}
              label={FORMATS[key]}
              selected={format === key}
              onPress={() => changeFilter(() => setFormat(toggle(format, key)))}
            />
          ))}
      </ChipRow>

      {format === 'food' ? (
        <>
          <Label>Кухня</Label>
          <ChipRow>
            {keysOf(CUISINES)
              .filter((key) => key !== 'other')
              .map((key) => (
                <Chip
                  key={key}
                  label={CUISINES[key]}
                  selected={cuisine === key}
                  onPress={() => changeFilter(() => setCuisine(toggle(cuisine, key)))}
                />
              ))}
          </ChipRow>
        </>
      ) : null}

      <Label>Бюджет — не дороже</Label>
      <ChipRow>
        {keysOf(BUDGETS).map((key) => (
          <Chip
            key={key}
            label={BUDGETS[key]}
            selected={budget === key}
            onPress={() => changeFilter(() => setBudget(toggle(budget, key)))}
          />
        ))}
      </ChipRow>

      <Button
        title="Подкинь идею"
        icon="shuffle"
        onPress={() => suggest(false)}
        loading={loading && !suggestion}
      />
      <ErrorText>{error}</ErrorText>
      {message ? <Subtitle>{message}</Subtitle> : null}

      {suggestion && item ? (
        <Card>
          <Text style={styles.source}>
            {suggestion.source === 'idea' ? 'Ваша идея' : 'Из подборки'}
          </Text>
          <Text style={styles.resultTitle}>{item.title}</Text>
          {item.description ? <Subtitle>{item.description}</Subtitle> : null}
          <Text style={{ color: colors.muted }}>
            {[
              FORMATS[item.format],
              item.cuisine ? CUISINES[item.cuisine] : null,
              item.budget ? BUDGETS[item.budget] : null,
            ]
              .filter(Boolean)
              .join('  ·  ')}
          </Text>
          <View style={{ gap: space.sm, marginTop: space.sm }}>
            {suggestion.source === 'catalog' ? (
              <Button
                title={saved ? 'Сохранено в идеи' : 'Сохранить в наши идеи'}
                icon={saved ? 'checkmark-circle-outline' : 'bookmark-outline'}
                variant="secondary"
                onPress={saveToIdeas}
                disabled={saved}
              />
            ) : null}
            <Button title="Ещё вариант" variant="ghost" onPress={() => suggest(true)} loading={loading} />
          </View>
        </Card>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  source: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.muted,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  resultTitle: { fontSize: 22, fontWeight: '700', color: colors.text },
});
