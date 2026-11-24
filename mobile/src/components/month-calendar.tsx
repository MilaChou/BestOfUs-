import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { isoOf, MONTHS_NOMINATIVE, todayIso } from '@/lib/dates';

import { colors, space } from './theme';
import { Icon } from './ui';

const WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

/**
 * A small month calendar. Days that have something planned get a dot
 * (red if something is overdue). Tapping a day selects it; tapping it again clears.
 */
export function MonthCalendar({
  busy,
  overdue,
  selected,
  onSelect,
}: {
  busy: Set<string>; // "2026-11-20"
  overdue: Set<string>;
  selected: string | null;
  onSelect: (day: string | null) => void;
}) {
  const today = todayIso();
  const [month, setMonth] = useState(() => {
    const d = new Date();
    return new Date(d.getFullYear(), d.getMonth(), 1);
  });

  // Monday-first grid: empty cells before the 1st, then the days of the month.
  const firstWeekday = (month.getDay() + 6) % 7;
  const daysInMonth = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
  const cells: (string | null)[] = [
    ...Array.from({ length: firstWeekday }, () => null),
    ...Array.from({ length: daysInMonth }, (_, i) =>
      isoOf(new Date(month.getFullYear(), month.getMonth(), i + 1)),
    ),
  ];
  while (cells.length % 7) cells.push(null);

  const shift = (n: number) => setMonth(new Date(month.getFullYear(), month.getMonth() + n, 1));

  return (
    <View style={styles.box}>
      <View style={styles.header}>
        <Pressable accessibilityRole="button" accessibilityLabel="Предыдущий месяц" hitSlop={10} onPress={() => shift(-1)}>
          <Icon name="chevron-back" size={20} />
        </Pressable>
        <Text style={styles.month}>
          {MONTHS_NOMINATIVE[month.getMonth()]} {month.getFullYear()}
        </Text>
        <Pressable accessibilityRole="button" accessibilityLabel="Следующий месяц" hitSlop={10} onPress={() => shift(1)}>
          <Icon name="chevron-forward" size={20} />
        </Pressable>
      </View>

      <View style={styles.row}>
        {WEEKDAYS.map((d) => (
          <Text key={d} style={styles.weekday}>
            {d}
          </Text>
        ))}
      </View>

      {Array.from({ length: cells.length / 7 }, (_, week) => (
        <View key={week} style={styles.row}>
          {cells.slice(week * 7, week * 7 + 7).map((day, i) => {
            if (!day) return <View key={i} style={styles.cell} />;
            const isSelected = day === selected;
            const isToday = day === today;
            return (
              <Pressable
                key={day}
                accessibilityRole="button"
                accessibilityState={{ selected: isSelected }}
                accessibilityLabel={day}
                onPress={() => onSelect(isSelected ? null : day)}
                style={styles.cell}>
                <View style={[styles.day, isToday && styles.today, isSelected && styles.selected]}>
                  <Text style={[styles.dayText, isSelected && { color: '#fff', fontWeight: '700' }]}>
                    {Number(day.slice(8, 10))}
                  </Text>
                </View>
                <View
                  style={[
                    styles.dot,
                    busy.has(day) && { backgroundColor: overdue.has(day) ? colors.danger : colors.black },
                  ]}
                />
              </Pressable>
            );
          })}
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { borderWidth: 1, borderColor: colors.border, borderRadius: 12, padding: space.sm, gap: 2 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: space.sm, paddingVertical: 6 },
  month: { fontSize: 15, fontWeight: '600', color: colors.text },
  row: { flexDirection: 'row' },
  weekday: { flex: 1, textAlign: 'center', fontSize: 11, color: colors.muted, paddingVertical: 4 },
  cell: { flex: 1, alignItems: 'center', paddingVertical: 2 },
  day: { width: 32, height: 32, borderRadius: 16, alignItems: 'center', justifyContent: 'center' },
  today: { borderWidth: 1, borderColor: colors.black },
  selected: { backgroundColor: colors.black },
  dayText: { fontSize: 14, color: colors.text },
  dot: { width: 5, height: 5, borderRadius: 3, marginTop: 1, backgroundColor: 'transparent' },
});
