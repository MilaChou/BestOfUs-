import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { AuthImage } from '@/components/auth-image';
import { TabHeader } from '@/components/tab-header';
import { colors, radius, space } from '@/components/theme';
import { Card, Empty, ErrorText, Fab, Icon, Loading, SectionTitle } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { formatDate, plural } from '@/lib/dates';
import type { Memory } from '@/lib/types';

export default function MemoriesScreen() {
  const [memories, setMemories] = useState<Memory[] | null>(null);
  const [onThisDay, setOnThisDay] = useState<Memory[]>([]);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const [all, today] = await Promise.all([
        api<Memory[]>('/couple/memories'),
        api<Memory[]>('/couple/memories/on-this-day'),
      ]);
      setMemories(all);
      setOnThisDay(today);
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

  const open = (m: Memory) => router.push({ pathname: '/memory/[id]', params: { id: String(m.id) } });

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={['top']}>
      {memories === null && !error ? (
        <Loading />
      ) : (
        <FlatList
          data={memories ?? []}
          keyExtractor={(m) => String(m.id)}
          contentContainerStyle={{ padding: space.md, paddingBottom: 100, gap: space.md }}
          ListHeaderComponent={
            <View style={{ gap: space.md }}>
              <TabHeader title="Воспоминания" />
              <ErrorText>{error}</ErrorText>
              {onThisDay.length ? (
                <>
                  <SectionTitle>В этот день</SectionTitle>
                  {onThisDay.map((m) => (
                    <Pressable key={m.id} onPress={() => open(m)}>
                      <Card style={{ backgroundColor: colors.surface, borderColor: colors.surface }}>
                        <Text style={styles.yearsAgo}>
                          {m.years_ago} {plural(m.years_ago, 'год', 'года', 'лет')} назад
                        </Text>
                        <Text style={styles.title}>{m.title}</Text>
                      </Card>
                    </Pressable>
                  ))}
                  <SectionTitle>Все</SectionTitle>
                </>
              ) : null}
            </View>
          }
          ListEmptyComponent={<Empty>Здесь будут ваши общие моменты — с датой, местом и фото.</Empty>}
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
            <Pressable onPress={() => open(item)}>
              <View style={styles.item}>
                {item.photos[0] ? (
                  <AuthImage path={item.photos[0].url} style={styles.cover} />
                ) : (
                  <View style={[styles.cover, styles.noPhoto]}>
                    <Icon name="image-outline" size={28} color={colors.muted} />
                  </View>
                )}
                <View style={{ gap: 2 }}>
                  <Text style={styles.title}>{item.title}</Text>
                  <Text style={styles.meta}>
                    {[formatDate(item.happened_on), item.place].filter(Boolean).join('  ·  ')}
                    {item.photos.length > 1 ? `  ·  ${item.photos.length} фото` : ''}
                  </Text>
                </View>
              </View>
            </Pressable>
          )}
        />
      )}
      <Fab label="Добавить воспоминание" onPress={() => router.push('/memory-form')} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  item: { gap: space.sm },
  cover: { width: '100%', aspectRatio: 16 / 10, borderRadius: radius.md, backgroundColor: colors.surface },
  noPhoto: { alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 17, fontWeight: '600', color: colors.text },
  meta: { fontSize: 13, color: colors.muted },
  yearsAgo: { fontSize: 12, fontWeight: '600', color: colors.muted, textTransform: 'uppercase', letterSpacing: 0.5 },
});
