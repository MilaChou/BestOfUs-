import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Alert, FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useAuth, usePartner } from '@/auth/auth-context';
import { MonthCalendar } from '@/components/month-calendar';
import { TabHeader } from '@/components/tab-header';
import { colors, space } from '@/components/theme';
import { Chip, ChipRow, Empty, ErrorText, Fab, Icon, Loading } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { formatDate, isoOf, relativeDay, todayIso } from '@/lib/dates';
import { TASK_CATEGORIES } from '@/lib/labels';
import type { Task } from '@/lib/types';

type Filter = 'all' | 'mine' | 'today' | 'week' | 'overdue' | 'done';
const FILTERS: Record<Filter, string> = {
  all: 'Все',
  mine: 'Мои',
  today: 'Сегодня',
  week: 'Неделя',
  overdue: 'Просрочено',
  done: 'Сделано',
};
function matches(task: Task, filter: Filter, myId: number | undefined): boolean {
  const today = todayIso();
  const weekEnd = isoOf(new Date(Date.now() + 7 * 86_400_000));
  switch (filter) {
    case 'all':
      return !task.is_done;
    case 'mine':
      return !task.is_done && (task.assignee_id === null || task.assignee_id === myId);
    case 'today':
      return !task.is_done && task.due_date === today;
    case 'week':
      return !task.is_done && !!task.due_date && task.due_date >= today && task.due_date <= weekEnd;
    case 'overdue':
      return task.is_overdue;
    case 'done':
      return task.is_done;
  }
}

export default function PlansScreen() {
  const { user } = useAuth();
  const partner = usePartner();
  const [filter, setFilter] = useState<Filter>('all');
  const [day, setDay] = useState<string | null>(null);
  const [tasks, setTasks] = useState<Task[] | null>(null);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      setTasks(await api<Task[]>('/couple/tasks'));
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

  async function toggle(task: Task) {
    try {
      const updated = await api<Task>(`/couple/tasks/${task.id}/${task.is_done ? 'undone' : 'done'}`, {
        method: 'POST',
      });
      setTasks((list) => list?.map((t) => (t.id === task.id ? updated : t)) ?? null);
    } catch (e) {
      Alert.alert('Не получилось', errorMessage(e));
    }
  }

  function whoLabel(task: Task): string {
    if (task.assignee_id === null) return 'Вместе';
    if (task.assignee_id === user?.id) return 'Я';
    return partner?.profile.name ?? 'Партнёр';
  }

  const all = tasks ?? [];
  const busy = new Set(all.filter((t) => t.due_date && !t.is_done).map((t) => t.due_date!));
  const overdue = new Set(all.filter((t) => t.is_overdue).map((t) => t.due_date!));
  const shown = day ? all.filter((t) => t.due_date === day) : all.filter((t) => matches(t, filter, user?.id));

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
      {tasks === null && !error ? (
        <Loading />
      ) : (
        <FlatList
          data={shown}
          keyExtractor={(t) => String(t.id)}
          contentContainerStyle={{ padding: space.md, paddingBottom: 100 }}
          ListHeaderComponent={
            <View style={{ gap: space.md, marginBottom: space.sm }}>
              <TabHeader title="Планы" />
              <MonthCalendar busy={busy} overdue={overdue} selected={day} onSelect={setDay} />
              {day ? (
                <Text style={styles.dayTitle}>{formatDate(day)}</Text>
              ) : (
                <ChipRow>
                  {(Object.keys(FILTERS) as Filter[]).map((key) => (
                    <Chip key={key} label={FILTERS[key]} selected={filter === key} onPress={() => setFilter(key)} />
                  ))}
                </ChipRow>
              )}
              <ErrorText>{error}</ErrorText>
            </View>
          }
          ListEmptyComponent={
            <Empty>
              {day
                ? 'На этот день ничего не запланировано.'
                : filter === 'done'
                  ? 'Пока ничего не сделано.'
                  : 'Всё сделано. Добавьте новый план кнопкой «+».'}
            </Empty>
          }
          ItemSeparatorComponent={() => <View style={styles.separator} />}
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
            <Pressable
              onPress={() => router.push({ pathname: '/task', params: { id: String(item.id) } })}
              style={({ pressed }) => [styles.row, pressed && { backgroundColor: colors.surface }]}>
              <Pressable
                accessibilityRole="checkbox"
                accessibilityState={{ checked: item.is_done }}
                accessibilityLabel={item.is_done ? 'Вернуть' : 'Сделано'}
                hitSlop={10}
                onPress={() => toggle(item)}>
                <Icon
                  name={item.is_done ? 'checkmark-circle' : 'ellipse-outline'}
                  size={26}
                  color={item.is_done ? colors.black : colors.muted}
                />
              </Pressable>
              <View style={{ flex: 1, gap: 3 }}>
                <Text style={[styles.title, item.is_done && styles.done]}>{item.title}</Text>
                <Text style={styles.meta}>
                  {[
                    whoLabel(item),
                    item.category ? TASK_CATEGORIES[item.category] : null,
                  ]
                    .filter(Boolean)
                    .join('  ·  ')}
                </Text>
              </View>
              {item.due_date ? (
                <Text style={[styles.due, item.is_overdue && { color: colors.danger, fontWeight: '600' }]}>
                  {relativeDay(item.due_date)}
                </Text>
              ) : null}
            </Pressable>
          )}
        />
      )}
      <Fab
        label="Добавить план"
        onPress={() => router.push(day ? { pathname: '/task', params: { due: day } } : '/task')}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: space.md, paddingVertical: 14, paddingHorizontal: 4 },
  separator: { height: 1, backgroundColor: colors.border, marginLeft: 46 },
  title: { fontSize: 16, color: colors.text, fontWeight: '500' },
  done: { textDecorationLine: 'line-through', color: colors.muted },
  meta: { fontSize: 13, color: colors.muted },
  due: { fontSize: 13, color: colors.muted },
  dayTitle: { fontSize: 17, fontWeight: '600', color: colors.text },
});
