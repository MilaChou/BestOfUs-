import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { Alert } from 'react-native';

import { Button, Chip, ChipRow, ErrorText, Input, Label, Loading, Screen, Subtitle } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { GIFT_TYPES, keysOf, PRIORITIES } from '@/lib/labels';
import type { GiftType, Wish, WishPriority } from '@/lib/types';

/** Add a wish to my wishlist (no id) or edit one (?id=5). */
export default function WishScreen() {
  const { id } = useLocalSearchParams<{ id?: string }>();
  const [loaded, setLoaded] = useState(!id);
  const [title, setTitle] = useState('');
  const [link, setLink] = useState('');
  const [price, setPrice] = useState('');
  const [note, setNote] = useState('');
  const [priority, setPriority] = useState<WishPriority>('nice');
  const [giftType, setGiftType] = useState<GiftType | null>(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    api<Wish[]>('/wishlist/me')
      .then((list) => {
        const w = list.find((x) => String(x.id) === id);
        if (!w) throw new Error();
        setTitle(w.title);
        setLink(w.link ?? '');
        setPrice(w.price === null ? '' : String(w.price));
        setNote(w.note ?? '');
        setPriority(w.priority);
        setGiftType(w.gift_type);
        setLoaded(true);
      })
      .catch((e) => setError(errorMessage(e, 'Желание не найдено')));
  }, [id]);

  async function save() {
    setError('');
    const priceNumber = price.trim() ? Number(price.replace(/\s/g, '')) : null;
    if (priceNumber !== null && (!Number.isInteger(priceNumber) || priceNumber < 0)) {
      setError('Цена — целое число в рублях');
      return;
    }
    setSaving(true);
    const json = {
      title: title.trim(),
      link: link.trim() || null,
      price: priceNumber,
      note: note.trim() || null,
      priority,
      gift_type: giftType,
    };
    try {
      await api(id ? `/wishlist/me/${id}` : '/wishlist/me', { method: id ? 'PATCH' : 'POST', json });
      router.back();
    } catch (e) {
      setError(errorMessage(e));
      setSaving(false);
    }
  }

  function remove() {
    Alert.alert('Удалить из вишлиста?', `«${title}»`, [
      { text: 'Отмена', style: 'cancel' },
      {
        text: 'Удалить',
        style: 'destructive',
        onPress: async () => {
          try {
            await api(`/wishlist/me/${id}`, { method: 'DELETE' });
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
      <Input label="Что хочется" value={title} onChangeText={setTitle} placeholder="Пазл на 1000 деталей" />
      <Input label="Ссылка" value={link} onChangeText={setLink} placeholder="https://" autoCapitalize="none" keyboardType="url" />
      <Input label="Цена, ₽" value={price} onChangeText={setPrice} placeholder="1500" keyboardType="number-pad" />
      <Input
        label="Комментарий"
        value={note}
        onChangeText={setNote}
        placeholder="Размер M, лучше синий"
        multiline
        style={{ minHeight: 70, paddingTop: 12, textAlignVertical: 'top' }}
      />
      <Label>Насколько хочется</Label>
      <ChipRow>
        {keysOf(PRIORITIES).map((key) => (
          <Chip key={key} label={PRIORITIES[key]} selected={priority === key} onPress={() => setPriority(key)} />
        ))}
      </ChipRow>
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
      <Subtitle>Партнёр увидит это желание. Если партнёр решит его подарить, вы об этом не узнаете — это сюрприз.</Subtitle>
      <ErrorText>{error}</ErrorText>
      <Button title="Сохранить" onPress={save} loading={saving} disabled={!title.trim()} />
      {id ? <Button title="Удалить" variant="ghost" icon="trash-outline" onPress={remove} /> : null}
    </Screen>
  );
}
