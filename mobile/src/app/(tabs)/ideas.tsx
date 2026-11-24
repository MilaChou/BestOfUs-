import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Alert, FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useAuth } from '@/auth/auth-context';
import { InviteBanner } from '@/components/invite-banner';
import { colors, space } from '@/components/theme';
import { TabHeader } from '@/components/tab-header';
import { Button, Card, Chip, ChipRow, ErrorText, Fab, Icon, Loading, Subtitle } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { BUDGETS, CUISINES, FORMATS, TIMES } from '@/lib/labels';
import type { Idea } from '@/lib/types';

type Filter = 'todo' | 'both' | 'done';
const FILTERS: Record<Filter, string> = { todo: 'Хотим сделать', both: 'Хотим оба', done: 'Сделали' };
const FILTER_QUERY: Record<Filter, Record<string, boolean>> = {
  todo: { is_done: false },
  both: { is_done: false, both_want: true },
  done: { is_done: true },
};

export default function IdeasScreen() {
  const { user } = useAuth();
  const [filter, setFilter] = useState<Filter>('todo');
  const [ideas, setIdeas] = useState<Idea[] | null>(null);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      setIdeas(await api<Idea[]>('/couple/ideas', { query: FILTER_QUERY[filter] }));
      setError('');
    } catch (e) {
      setError(errorMessage(e));
    }
  }, [filter]);

  // Reload every time the page is opened (e.g. after adding an idea).
  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  /** Run an action on an idea, then replace it in the list with the server's answer. */
  async function update(idea: Idea, path: string, method: 'POST' | 'DELETE' = 'POST') {
    try {
      const updated = await api<Idea>(`/couple/ideas/${idea.id}${path}`, {
        method,
        json: path === '/done' ? {} : undefined,
      });
      setIdeas((list) => list?.map((i) => (i.id === idea.id ? updated : i)) ?? null);
    } catch (e) {
      Alert.alert('Не получилось', errorMessage(e));
    }
  }

  /** A done idea -> a memory (title, review, date); then open it to add photos. */
  async function toMemory(idea: Idea) {
    try {
      const memory = await api<{ id: number }>(`/couple/memories/from-idea/${idea.id}`, {
        method: 'POST',
      });
      router.push({ pathname: '/memory/[id]', params: { id: String(memory.id) } });
    } catch (e) {
      Alert.alert('Не получилось', errorMessage(e));
    }
  }

  function confirmDelete(idea: Idea) {
    Alert.alert('Удалить идею?', `«${idea.title}»`, [
      { text: 'Отмена', style: 'cancel' },
      {
        text: 'Удалить',
        style: 'destructive',
        onPress: async () => {
          try {
            await api(`/couple/ideas/${idea.id}`, { method: 'DELETE' });
            setIdeas((list) => list?.filter((i) => i.id !== idea.id) ?? null);
          } catch (e) {
            Alert.alert('Не получилось', errorMessage(e));
          }
        },
      },
    ]);
  }

  const header = (
    <View style={{ gap: space.md, marginBottom: space.sm }}>
      <TabHeader title="Идеи" />
      <InviteBanner />
      <Button
        title="Подкинь идею"
        icon="shuffle"
        variant="secondary"
        onPress={() => router.push('/suggest')}
      />
      <ChipRow>
        {(Object.keys(FILTERS) as Filter[]).map((key) => (
          <Chip key={key} label={FILTERS[key]} selected={filter === key} onPress={() => setFilter(key)} />
        ))}
      </ChipRow>
      <ErrorText>{error}</ErrorText>
    </View>
  );

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
      {ideas === null && !error ? (
        <Loading />
      ) : (
        <FlatList
          data={ideas ?? []}
          keyExtractor={(idea) => String(idea.id)}
          contentContainerStyle={{ padding: space.md, paddingBottom: 100, gap: space.sm }}
          ListHeaderComponent={header}
          ListEmptyComponent={
            <Subtitle>
              {filter === 'done'
                ? 'Пока ничего не сделано — всё впереди.'
                : 'Идей пока нет. Добавьте первую или нажмите «Подкинь идею».'}
            </Subtitle>
          }
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              tintColor={colors.black}
              onRefresh={async () => {
                setRefreshing(true);
                await load();
                setRefreshing(false);
              }}
            />
          }
          renderItem={({ item }) => (
            <IdeaCard
              idea={item}
              iWant={!!user && item.wanted_by.includes(user.id)}
              onWant={(want) => update(item, '/want', want ? 'POST' : 'DELETE')}
              onDone={() => update(item, item.is_done ? '/undone' : '/done')}
              onDelete={() => confirmDelete(item)}
              onMemory={() => toMemory(item)}
            />
          )}
        />
      )}

      <Fab label="Добавить идею" onPress={() => router.push('/new-idea')} />
    </SafeAreaView>
  );
}

function IdeaCard({
  idea,
  iWant,
  onWant,
  onDone,
  onDelete,
  onMemory,
}: {
  idea: Idea;
  iWant: boolean;
  onWant: (want: boolean) => void;
  onDone: () => void;
  onDelete: () => void;
  onMemory: () => void;
}) {
  const tags = [
    FORMATS[idea.format],
    idea.cuisine ? CUISINES[idea.cuisine] : null,
    idea.budget ? BUDGETS[idea.budget] : null,
    ...idea.times_of_day.map((t) => TIMES[t]),
  ].filter(Boolean);

  return (
    <Pressable onLongPress={onDelete} delayLongPress={500}>
      <Card>
        <View style={styles.cardTop}>
          <Text style={[styles.ideaTitle, idea.is_done && styles.done]}>{idea.title}</Text>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel={iWant ? 'Убрать «хочу»' : 'Хочу тоже'}
            hitSlop={12}
            onPress={() => onWant(!iWant)}
            style={styles.heart}>
            <Icon
              name={iWant || idea.both_want ? 'heart' : 'heart-outline'}
              size={22}
              color={iWant || idea.both_want ? colors.heart : colors.muted}
            />
            {idea.both_want ? <Text style={styles.both}>оба</Text> : null}
          </Pressable>
        </View>
        {idea.description ? <Text style={styles.description}>{idea.description}</Text> : null}
        <Text style={styles.tags}>{tags.join('  ·  ')}</Text>
        <View style={styles.actions}>
          <Pressable accessibilityRole="button" onPress={onDone} hitSlop={8} style={styles.doneButton}>
            <Icon
              name={idea.is_done ? 'arrow-undo-outline' : 'checkmark-circle-outline'}
              size={18}
            />
            <Text style={styles.doneText}>{idea.is_done ? 'Вернуть в планы' : 'Сделали'}</Text>
          </Pressable>
          {idea.is_done ? (
            <Pressable accessibilityRole="button" onPress={onMemory} hitSlop={8} style={styles.doneButton}>
              <Icon name="images-outline" size={18} />
              <Text style={styles.doneText}>В воспоминания</Text>
            </Pressable>
          ) : null}
        </View>
      </Card>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  cardTop: { flexDirection: 'row', alignItems: 'flex-start', gap: space.sm },
  ideaTitle: { flex: 1, fontSize: 17, fontWeight: '600', color: colors.text },
  done: { textDecorationLine: 'line-through', color: colors.muted },
  heart: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  both: { fontSize: 12, fontWeight: '600', color: colors.heart },
  description: { fontSize: 15, color: colors.text, lineHeight: 21 },
  tags: { fontSize: 13, color: colors.muted },
  actions: { flexDirection: 'row', gap: space.lg, flexWrap: 'wrap' },
  doneButton: { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start', paddingTop: 4 },
  doneText: { fontSize: 14, fontWeight: '600', color: colors.text },
});
