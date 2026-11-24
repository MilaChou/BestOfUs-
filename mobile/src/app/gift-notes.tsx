import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Alert, FlatList, View } from 'react-native';

import { colors, space } from '@/components/theme';
import { Empty, ErrorText, Fab, Loading, Subtitle } from '@/components/ui';
import { NoteCard } from '@/components/wish-card';
import { api, errorMessage } from '@/lib/api';
import type { GiftNote } from '@/lib/types';

/** My secret gift ideas for the partner. Only I can see them. */
export default function GiftNotesScreen() {
  const [notes, setNotes] = useState<GiftNote[] | null>(null);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      setNotes(await api<GiftNote[]>('/gift-notes'));
      setError('');
    } catch (e) {
      setError(errorMessage(e));
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  async function toggle(note: GiftNote) {
    try {
      await api(`/gift-notes/${note.id}`, { method: 'PATCH', json: { is_gifted: !note.is_gifted } });
      await load();
    } catch (e) {
      Alert.alert('Не получилось', errorMessage(e));
    }
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      {notes === null && !error ? (
        <Loading />
      ) : (
        <FlatList
          data={notes ?? []}
          keyExtractor={(n) => String(n.id)}
          contentContainerStyle={{ padding: space.md, paddingBottom: 100, gap: space.sm }}
          ListHeaderComponent={
            <View style={{ marginBottom: space.sm }}>
              <Subtitle>Ваши тайные идеи подарков. Их видите только вы.</Subtitle>
              <ErrorText>{error}</ErrorText>
            </View>
          }
          ListEmptyComponent={<Empty>Услышали, что партнёр о чём-то мечтает? Запишите сюда, чтобы не забыть.</Empty>}
          renderItem={({ item }) => (
            <NoteCard
              note={item}
              onPress={() => router.push({ pathname: '/gift-note', params: { id: String(item.id) } })}
              onToggle={() => toggle(item)}
            />
          )}
        />
      )}
      <Fab label="Добавить заметку" onPress={() => router.push('/gift-note')} />
    </View>
  );
}
