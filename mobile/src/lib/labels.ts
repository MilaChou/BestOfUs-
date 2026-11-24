import type {
  Budget,
  Cuisine,
  Format,
  GiftType,
  NotificationCategory,
  ProfileField,
  TaskCategory,
  TimeOfDay,
  WishPriority,
} from './types';

export const FORMATS: Record<Format, string> = {
  home: 'Дома',
  walk: 'Прогулка',
  food: 'Поесть',
  active: 'Активный отдых',
  culture: 'Культура',
  trip: 'Поездка',
  other: 'Другое',
};

export const TIMES: Record<TimeOfDay, string> = {
  morning: 'Утро',
  day: 'День',
  evening: 'Вечер',
  night: 'Ночь',
};

export const BUDGETS: Record<Budget, string> = {
  free: 'Бесплатно',
  low: '₽',
  medium: '₽₽',
  high: '₽₽₽',
};

export const CUISINES: Record<Cuisine, string> = {
  russian: 'Русская',
  georgian: 'Грузинская',
  italian: 'Итальянская',
  french: 'Французская',
  japanese: 'Японская',
  chinese: 'Китайская',
  korean: 'Корейская',
  vietnamese: 'Вьетнамская',
  thai: 'Тайская',
  indian: 'Индийская',
  mexican: 'Мексиканская',
  american: 'Американская',
  other: 'Другая',
};

/** Object.keys with the right type, in the order written above. */
export function keysOf<K extends string>(labels: Record<K, string>): K[] {
  return Object.keys(labels) as K[];
}

export const TASK_CATEGORIES: Record<TaskCategory, string> = {
  shopping: 'Покупки',
  home: 'Дом',
  health: 'Здоровье',
  money: 'Деньги',
  errands: 'Дела',
  other: 'Другое',
};

export const GIFT_TYPES: Record<GiftType, string> = {
  home: 'Для дома',
  together: 'Провести время вместе',
  hobby: 'Для хобби',
  small_joy: 'Приятная мелочь',
  experience: 'Впечатление',
  beauty: 'Уход и красота',
  clothes: 'Одежда и аксессуары',
  tech: 'Техника',
  food: 'Вкусное',
};

export const PRIORITIES: Record<WishPriority, string> = {
  burning: 'Очень хочу',
  nice: 'Было бы классно',
  maybe: 'Не обязательно',
};

/** For "Что подарить?" the budget is an exact level, not "up to". */
export const GIFT_BUDGETS: Record<Budget, string> = {
  free: 'Своими руками',
  low: 'До 2 000 ₽',
  medium: '2 000–10 000 ₽',
  high: 'От 10 000 ₽',
};

export const NOTIFICATION_CATEGORIES: Record<NotificationCategory, string> = {
  couple: 'Партнёр присоединился',
  tasks: 'Планы',
  ideas: 'Идеи',
  memories: 'Воспоминания',
  wishlist: 'Вишлист партнёра',
  love_language: 'Тесты партнёра',
  birthday: 'День рождения партнёра',
  anniversary: 'Годовщины',
  tasks_due: 'Дела на сегодня',
  on_this_day: 'В этот день',
};

/** Profile fields grouped as in the profile screen. */
export const PROFILE_SECTIONS: { title: string; fields: { key: ProfileField; label: string; placeholder?: string; multiline?: boolean }[] }[] = [
  {
    title: 'Основное',
    fields: [
      { key: 'name', label: 'Имя' },
      { key: 'pet_name', label: 'Ласковое имя', placeholder: 'Как вас называет партнёр' },
      { key: 'birth_date', label: 'Дата рождения' },
    ],
  },
  {
    title: 'Для подарков',
    fields: [
      { key: 'ring_size', label: 'Размер кольца', placeholder: '16,5' },
      { key: 'shoe_size', label: 'Размер обуви', placeholder: '38' },
      { key: 'clothing_size_top', label: 'Размер одежды — верх', placeholder: 'S / 44' },
      { key: 'clothing_size_bottom', label: 'Размер одежды — низ', placeholder: 'S / 44' },
      { key: 'favorite_color', label: 'Любимый цвет' },
      { key: 'favorite_flowers', label: 'Любимые цветы' },
      { key: 'allergies', label: 'Аллергии', placeholder: 'На цветы, еду, косметику', multiline: true },
    ],
  },
  {
    title: 'Отношения',
    fields: [
      { key: 'how_to_support_me', label: 'Как меня поддержать', placeholder: 'Что помогает, когда грустно', multiline: true },
      { key: 'small_annoyances', label: 'Мелкие раздражители', placeholder: 'Что лучше не делать', multiline: true },
    ],
  },
  {
    title: 'Вкусы',
    fields: [
      { key: 'favorite_food', label: 'Любимая еда' },
      { key: 'favorite_drink', label: 'Любимый напиток' },
      { key: 'food_dislikes', label: 'Что не ем', multiline: true },
    ],
  },
];
