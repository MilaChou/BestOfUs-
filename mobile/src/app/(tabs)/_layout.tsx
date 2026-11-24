import { Tabs } from 'expo-router';
import { type ColorValue, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { colors, shadows, type } from '@/components/theme';
import { Icon, type IconName } from '@/components/ui';

function tabIcon(name: IconName, focusedName: IconName) {
  function TabIcon({ focused, color }: { focused: boolean; color: ColorValue }) {
    // The tab bar gives its colours as plain strings here.
    const tint = typeof color === 'string' ? color : undefined;
    return <Icon name={focused ? focusedName : name} color={tint} size={24} />;
  }
  return TabIcon;
}

/** "Мы" — the main tab: a black circle raised above the bar; the heart turns pink when open. */
function UsIcon({ focused }: { focused: boolean }) {
  return (
    <View
      style={{
        width: 52,
        height: 52,
        borderRadius: 26,
        backgroundColor: colors.black,
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: -26,
        borderWidth: 3,
        borderColor: colors.background,
        ...shadows.md,
      }}>
      <Icon name={focused ? 'heart' : 'heart-outline'} size={24} color={focused ? colors.heart : '#fff'} />
    </View>
  );
}

export default function TabsLayout() {
  const insets = useSafeAreaInsets();
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.black,
        tabBarInactiveTintColor: colors.subtle,
        tabBarStyle: {
          backgroundColor: colors.background,
          borderTopWidth: 0,
          // ~64 pt bar (+ room for the label) + the phone's own bottom area (gesture bar / home indicator)
          height: 70 + insets.bottom,
          paddingTop: 8,
          paddingBottom: Math.max(insets.bottom, 12),
          ...shadows.up,
        },
        tabBarLabelStyle: type.tab,
      }}>
      <Tabs.Screen name="ideas" options={{ title: 'Идеи', tabBarIcon: tabIcon('bulb-outline', 'bulb') }} />
      <Tabs.Screen
        name="plans"
        options={{ title: 'Планы', tabBarIcon: tabIcon('calendar-clear-outline', 'calendar-clear') }}
      />
      {/* index.tsx opens first when the app starts */}
      <Tabs.Screen name="index" options={{ title: 'Мы', tabBarIcon: UsIcon }} />
      <Tabs.Screen name="memories" options={{ title: 'Моменты', tabBarIcon: tabIcon('images-outline', 'images') }} />
      <Tabs.Screen name="settings" options={{ title: 'Настройки', tabBarIcon: tabIcon('settings-outline', 'settings') }} />
    </Tabs>
  );
}
