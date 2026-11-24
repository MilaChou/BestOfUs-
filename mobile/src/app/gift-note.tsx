import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { Alert } from 'react-native';

import { Button, Chip, ChipRow, ErrorText, Input, Label, Loading, Screen, Subtitle } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { GIFT_TYPES, keysOf } from '@/lib/labels';
import type { GiftNote, GiftType } from '@/lib/types';

/** A secret "what to gift" note, visible only to its author. */
export default function GiftNoteScreen() {
  const { id } = useLocalSearchParams<{ id?: string }>();
  const [loaded, setLoaded] = useState(!id);
  const [title, setTitle] = useState('');
  const [note, setNote] = useState('');
  const [link, setLink] = useState('');
  const [price, setPrice] = useState('');
  const [giftType, setGiftType] = useState<GiftType | null>(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    api<GiftNote[]>('/gift-notes')
      .then((list) => {
        const n = list.find((x) => String(x.id) === id);
        if (!n) throw new Error();
        setTitle(n.title);
        setNote(n.note ?? '');
        setLink(n.link ?? '');
        setPrice(n.price === null ? '' : String(n.price));
        setGiftType(n.gift_type);
        setLoaded(true);
      })
      .catch((e) => setError(errorMessage(e, 'Заметка не найдена')));
  }, [id]);

  async function save() {
    setError('');
    const priceNumber = price.trim() ? Number(price.replace(/\s/g, '')) : null;
    if (priceNumber !== null && (!Number.isInteger(priceNumber) || priceNumber < 0)) {
      setError('Цена — целое число в рублях');
      return;
    }
    setSaving(true);
    const json = { title: title.trim(), note: note.trim() || null, link: link.trim() || null, price: priceNumber, gift_type: giftType };
    try {
      await api(id ? `/gift-notes/${id}` : '/gift-notes', { method: id ? 'PATCH' : 'POST', json });
      router.back();
    } catch (e) {
      setError(errorMessage(e));
      setSaving(false);
    }
  }

  function remove() {
    Alert.alert('Удалить заметку?', `«${title}»`, [
      { text: 'Отмена', style: 'cancel' },
      {
        text: 'Удалить',
        style: 'destructive',
        onPress: async () => {
          try {
            await api(`/gift-notes/${id}`, { method: 'DELETE' });
            router.back();
          } catch (e) {
            setError(errorMessage(e));
          }
        },
      },
    ]);
  }

  if (!loaded) return <Screen topInset={false}>{error ? <ErrorText>{error}</ErrorText> : <Loading />}</Screen>;

  return (
    <Screen topInset={false}>
      <Subtitle>Эту заметку видите только вы.</Subtitle>
      <Input label="Идея подарка" value={title} onChangeText={setTitle} placeholder="Кружка с котом, которую видели в кафе" />
      <Input
        label="Подробности"
        value={note}
        onChangeText={setNote}
        multiline
        style={{ minHeight: 70, paddingTop: 12, textAlignVertical: 'top' }}
      />
      <Input label="Ссылка" value={link} onChangeText={setLink} placeholder="https://" autoCapitalize="none" keyboardType="url" />
      <Input label="Цена, ₽" value={price} onChangeText={setPrice} keyboardType="number-pad" />
      <Label>Тип подарка</Label>
      <ChipRow>
        {keysOf(GIFT_TYPES).map((key) => (
          <Chip
            key={key}
            label={GIFT_TYPES[key]}
            selected={giftType === key}
            onPress={() => setGiftType(giftType === key ? null : key)}
          />
        ))}
      </ChipRow>
      <ErrorText>{error}</ErrorText>
      <Button title="Сохранить" onPress={save} loading={saving} disabled={!title.trim()} />
      {id ? <Button title="Удалить" variant="ghost" icon="trash-outline" onPress={remove} /> : null}
    </Screen>
  );
}
