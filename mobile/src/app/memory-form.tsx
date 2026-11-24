import type { ImagePickerAsset } from 'expo-image-picker';
import { Image } from 'expo-image';
import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { ScrollView, View } from 'react-native';

import { radius, space } from '@/components/theme';
import { Button, DateInput, ErrorText, Input, Label, Loading, Screen } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { inputToIso, isoToInput, todayIso } from '@/lib/dates';
import { pickPhotos, uploadPhotos } from '@/lib/photos';
import type { Memory } from '@/lib/types';

const MAX_PHOTOS = 10;

/** New memory (with photos) or editing one (?id=5; photos are managed on the memory page). */
export default function MemoryFormScreen() {
  const { id } = useLocalSearchParams<{ id?: string }>();
  const [loaded, setLoaded] = useState(!id);
  const [title, setTitle] = useState('');
  const [date, setDate] = useState(isoToInput(todayIso()));
  const [place, setPlace] = useState('');
  const [description, setDescription] = useState('');
  const [photos, setPhotos] = useState<ImagePickerAsset[]>([]);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    api<Memory>(`/couple/memories/${id}`)
      .then((m) => {
        setTitle(m.title);
        setDate(isoToInput(m.happened_on));
        setPlace(m.place ?? '');
        setDescription(m.description ?? '');
        setLoaded(true);
      })
      .catch((e) => setError(errorMessage(e)));
  }, [id]);

  async function addPhotos() {
    const picked = await pickPhotos(MAX_PHOTOS - photos.length);
    setPhotos((p) => [...p, ...picked].slice(0, MAX_PHOTOS));
  }

  async function save() {
    setError('');
    const iso = inputToIso(date);
    if (!iso) {
      setError('Дата — в формате ДД.ММ.ГГГГ');
      return;
    }
    setSaving(true);
    const json = {
      title: title.trim(),
      happened_on: iso,
      place: place.trim() || null,
      description: description.trim() || null,
    };
    try {
      if (id) {
        await api(`/couple/memories/${id}`, { method: 'PATCH', json });
        router.back();
        return;
      }
      const memory = await api<Memory>('/couple/memories', { method: 'POST', json });
      if (photos.length) await uploadPhotos(memory.id, photos);
      router.replace({ pathname: '/memory/[id]', params: { id: String(memory.id) } });
    } catch (e) {
      setError(errorMessage(e));
      setSaving(false);
    }
  }

  if (!loaded) return <Screen topInset={false}>{error ? <ErrorText>{error}</ErrorText> : <Loading />}</Screen>;

  return (
    <Screen topInset={false}>
      <Input label="Что было" value={title} onChangeText={setTitle} placeholder="Первое свидание" />
      <DateInput label="Когда" value={date} onChangeText={setDate} />
      <Input label="Где" value={place} onChangeText={setPlace} placeholder="Кофейня на углу" />
      <Input
        label="Как это было"
        value={description}
        onChangeText={setDescription}
        multiline
        style={{ minHeight: 100, paddingTop: 12, textAlignVertical: 'top' }}
      />

      {!id ? (
        <>
          <Label>Фото ({photos.length} из {MAX_PHOTOS})</Label>
          {photos.length ? (
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={{ flexDirection: 'row', gap: space.sm }}>
                {photos.map((p) => (
                  <Image key={p.uri} source={{ uri: p.uri }} style={{ width: 90, height: 90, borderRadius: radius.sm }} />
                ))}
              </View>
            </ScrollView>
          ) : null}
          {photos.length < MAX_PHOTOS ? (
            <Button title="Добавить фото" icon="images-outline" variant="secondary" onPress={addPhotos} />
          ) : null}
        </>
      ) : null}

      <ErrorText>{error}</ErrorText>
      <Button title="Сохранить" onPress={save} loading={saving} disabled={!title.trim()} />
    </Screen>
  );
}
