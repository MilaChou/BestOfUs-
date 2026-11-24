/** Shapes of the data the backend sends — kept in sync with app/schemas/*.py. */

// --- Ideas -----------------------------------------------------------------

export type TimeOfDay = 'morning' | 'day' | 'evening' | 'night';
export type Format = 'home' | 'walk' | 'food' | 'active' | 'culture' | 'trip' | 'other';
export type Cuisine =
  | 'russian'
  | 'georgian'
  | 'italian'
  | 'french'
  | 'japanese'
  | 'chinese'
  | 'korean'
  | 'vietnamese'
  | 'thai'
  | 'indian'
  | 'mexican'
  | 'american'
  | 'other';
export type Budget = 'free' | 'low' | 'medium' | 'high';

export type Idea = {
  id: number;
  title: string;
  description: string | null;
  link: string | null;
  format: Format;
  cuisine: Cuisine | null;
  budget: Budget | null;
  times_of_day: TimeOfDay[];
  author_id: number | null;
  wanted_by: number[];
  both_want: boolean;
  is_done: boolean;
  rating: number | null;
  catalog_id: string | null;
};

export type CatalogActivity = {
  id: string;
  title: string;
  description: string;
  format: Format;
  cuisine: Cuisine | null;
  budget: Budget;
  times_of_day: TimeOfDay[];
};

export type Suggestion =
  | { source: 'idea'; idea: Idea; activity: null }
  | { source: 'catalog'; idea: null; activity: CatalogActivity };

// --- People ----------------------------------------------------------------

export type Profile = {
  name: string;
  pet_name: string | null;
  avatar_url: string | null;
  birth_date: string | null; // "2000-05-14"
  ring_size: string | null;
  shoe_size: string | null;
  clothing_size_top: string | null;
  clothing_size_bottom: string | null;
  favorite_color: string | null;
  favorite_flowers: string | null;
  allergies: string | null;
  how_to_support_me: string | null;
  small_annoyances: string | null;
  favorite_food: string | null;
  favorite_drink: string | null;
  food_dislikes: string | null;
};

export type ProfileField = Exclude<keyof Profile, 'avatar_url'>;

export type User = {
  id: number;
  email: string;
  created_at: string;
  profile: Profile;
};

export type Member = { id: number; profile: Profile };

export type Couple = {
  id: number;
  name: string | null;
  together_since: string | null;
  invite_code: string | null;
  members: Member[];
  days_together: number | null;
};

// --- Plans -----------------------------------------------------------------

export type TaskCategory = 'shopping' | 'home' | 'health' | 'money' | 'errands' | 'other';

export type Task = {
  id: number;
  title: string;
  note: string | null;
  category: TaskCategory | null;
  due_date: string | null;
  author_id: number | null;
  assignee_id: number | null; // null = both of us
  is_done: boolean;
  done_at: string | null;
  done_by_id: number | null;
  is_overdue: boolean;
};

// --- Gifts -----------------------------------------------------------------

export type GiftType =
  | 'home'
  | 'together'
  | 'hobby'
  | 'small_joy'
  | 'experience'
  | 'beauty'
  | 'clothes'
  | 'tech'
  | 'food';
export type WishPriority = 'burning' | 'nice' | 'maybe';

export type Wish = {
  id: number;
  title: string;
  link: string | null;
  price: number | null;
  image_url: string | null;
  note: string | null;
  priority: WishPriority;
  gift_type: GiftType | null;
  is_received: boolean;
  budget: Budget | null;
  is_reserved?: boolean; // only in the partner's view
};

export type GiftNote = {
  id: number;
  title: string;
  note: string | null;
  link: string | null;
  price: number | null;
  gift_type: GiftType | null;
  catalog_id: string | null;
  is_gifted: boolean;
  budget: Budget | null;
};

export type CatalogGift = {
  id: string;
  title: string;
  description: string;
  gift_type: GiftType;
  budget: Budget;
  personalized: boolean;
  hint: string | null;
};

export type GiftSuggestion = {
  source: 'wishlist' | 'note' | 'catalog';
  wish: Wish | null;
  note: GiftNote | null;
  gift: CatalogGift | null;
  warning: string | null;
};

// --- Memories --------------------------------------------------------------

export type Photo = { id: number; memory_id: number; content_type: string; url: string };

export type Memory = {
  id: number;
  title: string;
  description: string | null;
  happened_on: string;
  place: string | null;
  author_id: number | null;
  idea_id: number | null;
  photos: Photo[];
  years_ago: number;
};

// --- Tests ("Язык любви", "Язык извинений") -------------------------------

export type TestId = 'love' | 'apology';

export type TestInfo = {
  id: TestId;
  title: string;
  subtitle: string;
  questions_count: number;
  my_leading: string[]; // titles; empty if not taken
};

export type TestQuestions = {
  id: TestId;
  title: string;
  prompt: string;
  questions: { id: number; a: string; b: string }[];
};

export type TestResult = {
  test_id: TestId;
  title: string;
  scores: { key: string; title: string; points: number; max: number; percent: number }[];
  leading: string[]; // category keys; several only on a tie
  advice_title: string;
  advice: { key: string; title: string; description: string; advice: string }[];
  taken_at: string;
};

// --- Notifications ---------------------------------------------------------

export type NotificationCategory =
  | 'couple'
  | 'tasks'
  | 'ideas'
  | 'memories'
  | 'wishlist'
  | 'love_language'
  | 'birthday'
  | 'anniversary'
  | 'tasks_due'
  | 'on_this_day';

export type AppNotification = {
  id: number;
  type: string;
  title: string;
  body: string;
  data: Record<string, string | number>;
  is_read: boolean;
  created_at: string;
};
