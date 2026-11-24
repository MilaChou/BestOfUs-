import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { colors, space } from '@/components/theme';
import { Button, Card, Chip, ChipRow, ErrorText, Icon, Label, Screen, Subtitle } from '@/components/ui';
import { api, ApiError, errorMessage } from '@/lib/api';
import { formatPrice } from '@/lib/dates';
import { GIFT_BUDGETS, GIFT_TYPES, keysOf } from '@/lib/labels';
import type { Budget, GiftSuggestion, GiftType } from '@/lib/types';

const SOURCE: Record<GiftSuggestion['source'], string> = {
  wishlist: 'Из вишлиста партнёра',
  note: 'Ваша заметка',
  catalog: 'Из подборки',
};

export default function GiftSuggestScreen() {
  const [budget, setBudget] = useState<Budget | null>(null);
  const [giftType, setGiftType] = useState<GiftType | null>(null);
  const [result, setResult] = useState<GiftSuggestion | null>(null);
  const [seen, setSeen] = useState<{ wishes: number[]; notes: number[]; catalog: string[] }>({
    wishes: [],
    notes: [],
    catalog: [],
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState('');

  function changeFilter(apply: () => void) {
    apply();
    setResult(null);
    setSeen({ wishes: [], notes: [], catalog: [] });
    setMessage('');
  }

  async function suggest(more: boolean) {
    setError('');
    setMessage('');
    setDone('');
    setLoading(true);
    const skip = more ? seen : { wishes: [], notes: [], catalog: [] };
    try {
      const r = await api<GiftSuggestion>('/gifts/suggest', {
        query: {
          budget,
          gift_type: giftType,
          exclude_wishes: skip.wishes,
          exclude_notes: skip.notes,
          exclude_catalog: skip.catalog,
        },
      });
      setResult(r);
      setSeen({
        wishes: r.wish ? [...skip.wishes, r.wish.id] : skip.wishes,
        notes: r.note ? [...skip.notes, r.note.id] : skip.notes,
        catalog: r.gift ? [...skip.catalog, r.gift.id] : skip.catalog,
      });
    } catch (e) {
      setResult(null);
      if (e instanceof ApiError && e.status === 404) {
        setMessage(more ? 'Варианты закончились. Попробуйте другие фильтры.' : 'Ничего не нашлось — уберите часть фильтров.');
      } else setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  }

  async function reserve() {
    if (!result?.wish) return;
    try {
      await api(`/wishlist/partner/${result.wish.id}/reserve`, { method: 'POST' });
      setDone('Забронировано — партнёр не узнает');
    } catch (e) {
      setError(errorMessage(e));
    }
  }

  async function saveNote() {
    if (!result?.gift) return;
    try {
      await api(`/gift-notes/from-catalog/${result.gift.id}`, { method: 'POST' });
      setDone('Сохранено в ваши заметки');
    } catch (e) {
      setError(errorMessage(e));
    }
  }

  const title = result?.wish?.title ?? result?.note?.title ?? result?.gift?.title;
  const description = result?.wish?.note ?? result?.note?.note ?? result?.gift?.description;
  const price = result?.wish?.price ?? result?.note?.price ?? null;

  return (
    <Screen topInset={false}>
      <Subtitle>
        Сначала — то, что партнёр сам хочет, потом ваши заметки, потом идеи из его профиля и подборки.
      </Subtitle>

      <Label>Бюджет</Label>
      <ChipRow>
        {keysOf(GIFT_BUDGETS).map((key) => (
          <Chip
            key={key}
            label={GIFT_BUDGETS[key]}
            selected={budget === key}
            onPress={() => changeFilter(() => setBudget(budget === key ? null : key))}
          />
        ))}
      </ChipRow>

      <Label>Какой подарок</Label>
      <ChipRow>
        {keysOf(GIFT_TYPES).map((key) => (
          <Chip
            key={key}
            label={GIFT_TYPES[key]}
            selected={giftType === key}
            onPress={() => changeFilter(() => setGiftType(giftType === key ? null : key))}
          />
        ))}
      </ChipRow>

      <Button title="Подобрать подарок" icon="sparkles-outline" onPress={() => suggest(false)} loading={loading && !result} />
      <ErrorText>{error}</ErrorText>
      {message ? <Subtitle>{message}</Subtitle> : null}

      {result && title ? (
        <Card>
          <Text style={styles.source}>
            {result.gift?.personalized ? 'Из профиля партнёра' : SOURCE[result.source]}
          </Text>
          <Text style={styles.title}>{title}</Text>
          {description ? <Subtitle>{description}</Subtitle> : null}
          {result.gift?.hint ? <Text style={styles.hint}>{result.gift.hint}</Text> : null}
          {price !== null ? <Text style={styles.hint}>{formatPrice(price)}</Text> : null}
          {result.warning ? (
            <View style={styles.warning}>
              <Icon name="alert-circle-outline" size={18} color={colors.danger} />
              <Text style={styles.warningText}>{result.warning}</Text>
            </View>
          ) : null}
          <View style={{ gap: space.sm, marginTop: space.sm }}>
            {done ? (
              <Text style={styles.hint}>{done}</Text>
            ) : result.source === 'wishlist' ? (
              <Button title="Я подарю" icon="gift-outline" variant="secondary" onPress={reserve} />
            ) : result.source === 'catalog' ? (
              <Button title="Сохранить в заметки" icon="bookmark-outline" variant="secondary" onPress={saveNote} />
            ) : null}
            <Button title="Ещё вариант" variant="ghost" onPress={() => suggest(true)} loading={loading} />
          </View>
        </Card>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  source: { fontSize: 12, fontWeight: '600', color: colors.muted, textTransform: 'uppercase', letterSpacing: 0.5 },
  title: { fontSize: 22, fontWeight: '700', color: colors.text },
  hint: { fontSize: 14, color: colors.muted },
  warning: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
  warningText: { flex: 1, fontSize: 14, color: colors.danger },
});
