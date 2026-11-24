import { router, Stack, useFocusEffect, useLocalSearchParams } from 'expo-router';
import { useCallback, useState } from 'react';
import { Alert, Pressable, StyleSheet, Text, useWindowDimensions, View } from 'react-native';

import { AuthImage } from '@/components/auth-image';
import { colors, radius, space } from '@/components/theme';
import { Button, ErrorText, IconButton, Loading, Screen, Subtitle } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { formatDate } from '@/lib/dates';
import { pickPhotos, uploadPhotos } from '@/lib/photos';
import type { Memory, Photo } from '@/lib/types';

const MAX_PHOTOS = 10;

export default function MemoryScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { width } = useWindowDimensions();
  const [memory, setMemory] = useState<Memory | null>(null);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);

  useFocusEffect(
    useCallback(() => {
      api<Memory>(`/couple/memories/${id}`).then(setMemory).catch((e) => setError(errorMessage(e)));
    }, [id]),
  );

  async function addPhotos() {
    if (!memory) return;
    const picked = await pickPhotos(MAX_PHOTOS - memory.photos.length);
    if (!picked.length) return;
    setUploading(true);
    try {
      setMemory(await uploadPhotos(memory.id, picked));
    } catch (e) {
      Alert.alert('Не получилось загрузить', errorMessage(e));
    } finally {
      setUploading(false);
    }
  }

  function removePhoto(photo: Photo) {
    Alert.alert('Удалить фото?', '', [
      { text: 'Отмена', style: 'cancel' },
      {
        text: 'Удалить',
        style: 'destructive',
        onPress: async () => {
          try {
            await api(photo.url.replace('/api/v1', ''), { method: 'DELETE' });
            setMemory((m) => (m ? { ...m, photos: m.photos.filter((p) => p.id !== photo.id) } : m));
          } catch (e) {
            Alert.alert('Не получилось', errorMessage(e));
          }
        },
      },
    ]);
  }

  function removeMemory() {
    Alert.alert('Удалить воспоминание?', 'Вместе с фото. Это нельзя отменить.', [
      { text: 'Отмена', style: 'cancel' },
      {
        text: 'Удалить',
        style: 'destructive',
        onPress: async () => {
          try {
            await api(`/couple/memories/${id}`, { method: 'DELETE' });
            router.back();
          } catch (e) {
            Alert.alert('Не получилось', errorMessage(e));
          }
        },
      },
    ]);
  }

  if (!memory) return <Screen topInset={false}>{error ? <ErrorText>{error}</ErrorText> : <Loading />}</Screen>;

  const size = (Math.min(width, 600) - space.md * 2 - space.sm) / 2;

  return (
    <Screen topInset={false}>
      <Stack.Screen
        options={{
          title: '',
          headerRight: () => (
            <IconButton
              name="create-outline"
              label="Изменить"
              onPress={() => router.push({ pathname: '/memory-form', params: { id } })}
            />
          ),
        }}
      />
      <Text style={styles.title}>{memory.title}</Text>
      <Subtitle>{[formatDate(memory.happened_on), memory.place].filter(Boolean).join('  ·  ')}</Subtitle>
      {memory.description ? <Text style={styles.description}>{memory.description}</Text> : null}

      {memory.photos.length ? (
        <View style={styles.grid}>
          {memory.photos.map((p) => (
            <Pressable key={p.id} onLongPress={() => removePhoto(p)} delayLongPress={500}>
              <AuthImage path={p.url} style={{ width: size, height: size, borderRadius: radius.sm }} />
            </Pressable>
          ))}
        </View>
      ) : null}
      {memory.photos.length ? <Subtitle>Чтобы удалить фото, нажмите на него и подержите.</Subtitle> : null}

      {memory.photos.length < MAX_PHOTOS ? (
        <Button title="Добавить фото" icon="images-outline" variant="secondary" onPress={addPhotos} loading={uploading} />
      ) : null}
      <Button title="Удалить воспоминание" icon="trash-outline" variant="ghost" onPress={removeMemory} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 26, fontWeight: '700', color: colors.text },
  description: { fontSize: 16, color: colors.text, lineHeight: 23 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: space.sm },
});
