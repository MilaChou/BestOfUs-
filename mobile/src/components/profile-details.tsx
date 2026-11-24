import { StyleSheet, Text, View } from 'react-native';

import { PROFILE_SECTIONS } from '@/lib/labels';
import type { Profile } from '@/lib/types';

import { colors, space } from './theme';
import { Card, Empty, SectionTitle } from './ui';

/** The filled-in profile sections (sizes, favourites, ...), the same for me and my partner. */
export function ProfileDetails({ profile, emptyText }: { profile: Profile; emptyText: string }) {
  const sections = PROFILE_SECTIONS.map((section) => ({
    ...section,
    fields: section.fields.filter(
      (f) => !['name', 'pet_name', 'birth_date'].includes(f.key) && profile[f.key],
    ),
  })).filter((section) => section.fields.length > 0);

  if (sections.length === 0) return <Empty>{emptyText}</Empty>;

  return (
    <>
      {sections.map((section) => (
        <View key={section.title} style={{ gap: space.sm }}>
          <SectionTitle>{section.title}</SectionTitle>
          <Card>
            {section.fields.map((f) => (
              <View key={f.key} style={{ gap: 2, paddingVertical: 4 }}>
                <Text style={styles.label}>{f.label}</Text>
                <Text style={styles.value}>{profile[f.key]}</Text>
              </View>
            ))}
          </Card>
        </View>
      ))}
    </>
  );
}

const styles = StyleSheet.create({
  label: { fontSize: 13, color: colors.muted },
  value: { fontSize: 16, color: colors.text },
});
