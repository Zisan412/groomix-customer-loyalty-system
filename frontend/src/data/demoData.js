export const categories = ['All products', 'Face Care', 'Hair Care', 'Beard & Grooming', 'Body Care'];

export const products = [
  { id: 1, name: 'Daily Reset Face Wash', category: 'Face Care', price: 480, units: 24, stock: 186, cost: 312, color: 'sage', tag: 'Bestseller', sku: 'FC-001', emoji: '🧴' },
  { id: 2, name: 'Polish & Purify Scrub', category: 'Face Care', price: 540, units: 24, stock: 92, cost: 348, color: 'sand', sku: 'FC-002', emoji: '🫧' },
  { id: 3, name: 'Cloudsoft Daily Moisturizer', category: 'Face Care', price: 720, units: 24, stock: 134, cost: 455, color: 'blue', sku: 'FC-003', emoji: '✨' },
  { id: 4, name: 'Sunveil SPF 50 Sunscreen', category: 'Face Care', price: 840, units: 24, stock: 74, cost: 594, color: 'peach', tag: 'New', sku: 'FC-004', emoji: '☀️' },
  { id: 5, name: 'Daily Strength Shampoo', category: 'Hair Care', price: 960, units: 24, stock: 220, cost: 612, color: 'blue', tag: 'Bestseller', sku: 'HC-001', emoji: '🧴' },
  { id: 6, name: 'Smooth Finish Conditioner', category: 'Hair Care', price: 900, units: 24, stock: 118, cost: 576, color: 'sage', sku: 'HC-002', emoji: '🌿' },
  { id: 7, name: 'Repair Ritual Hair Serum', category: 'Hair Care', price: 1080, units: 24, stock: 66, cost: 702, color: 'peach', sku: 'HC-003', emoji: '💧' },
  { id: 8, name: 'Root Revival Hair Oil', category: 'Hair Care', price: 780, units: 24, stock: 142, cost: 498, color: 'sand', sku: 'HC-004', emoji: '🌱' },
  { id: 9, name: 'Beard & Beyond Oil', category: 'Beard & Grooming', price: 660, units: 24, stock: 85, cost: 415, color: 'sand', sku: 'BG-001', emoji: '🧔' },
  { id: 10, name: 'Gentleman Beard Wash', category: 'Beard & Grooming', price: 600, units: 24, stock: 108, cost: 390, color: 'blue', sku: 'BG-002', emoji: '🫧' },
  { id: 11, name: 'Sculpt & Shape Beard Cream', category: 'Beard & Grooming', price: 720, units: 24, stock: 48, cost: 468, color: 'sage', sku: 'BG-003', emoji: '✨' },
  { id: 12, name: 'Fresh Start Body Wash', category: 'Body Care', price: 840, units: 24, stock: 174, cost: 530, color: 'blue', sku: 'BC-001', emoji: '🧴' },
  { id: 13, name: 'Everyday Body Lotion', category: 'Body Care', price: 900, units: 24, stock: 95, cost: 585, color: 'peach', sku: 'BC-002', emoji: '🌼' },
  { id: 14, name: 'All-day Deodorant', category: 'Body Care', price: 600, units: 24, stock: 156, cost: 372, color: 'sage', sku: 'BC-003', emoji: '🍃' },
];

export const orders = [
  { id: 'GR-24081', wholesaler: 'Aarav Wellness Mart', date: '24 Nov 2026', amount: 38400, status: 'Pending approval', payment: 'Advance', items: 4 },
  { id: 'GR-24080', wholesaler: 'The Daily Edit', date: '23 Nov 2026', amount: 21600, status: 'Processing', payment: 'Paid', items: 3 },
  { id: 'GR-24079', wholesaler: 'Urban Grooming Co.', date: '22 Nov 2026', amount: 52800, status: 'Dispatched', payment: 'Credit', items: 6 },
  { id: 'GR-24078', wholesaler: 'Glow & Go Retail', date: '21 Nov 2026', amount: 14400, status: 'Delivered', payment: 'Paid', items: 2 },
  { id: 'GR-24077', wholesaler: 'The Good Shelf', date: '20 Nov 2026', amount: 28800, status: 'Delivered', payment: 'Paid', items: 5 },
  { id: 'GR-24076', wholesaler: 'Aarav Wellness Mart', date: '18 Nov 2026', amount: 19200, status: 'Cancelled', payment: 'Refunded', items: 3 },
  { id: 'GR-24075', wholesaler: 'Aarav Wellness Mart', date: '17 Nov 2026', amount: 31200, status: 'Approved', payment: 'Paid', items: 4 },
];

export const wholesalers = [
  { name: 'Aarav Wellness Mart', initials: 'AW', city: 'Pune, Maharashtra', orders: 18, sales: 386400, credit: '₹1,20,000 / ₹2,00,000', status: 'Active' },
  { name: 'The Daily Edit', initials: 'DE', city: 'Mumbai, Maharashtra', orders: 12, sales: 264000, credit: 'No facility', status: 'Active' },
  { name: 'Urban Grooming Co.', initials: 'UG', city: 'Bengaluru, Karnataka', orders: 26, sales: 712800, credit: '₹2,80,000 / ₹3,00,000', status: 'Active' },
  { name: 'Glow & Go Retail', initials: 'GG', city: 'Hyderabad, Telangana', orders: 9, sales: 158400, credit: '₹0 / ₹1,00,000', status: 'Review' },
  { name: 'The Good Shelf', initials: 'GS', city: 'Jaipur, Rajasthan', orders: 15, sales: 345600, credit: 'No facility', status: 'Active' },
];

export const rewardItems = [
  { id: 1, name: 'Groomix Everyday Essentials Kit', points: 12000, stock: 18, type: 'Grooming kit', emoji: '🎁', color: 'peach' },
  { id: 2, name: 'Signature Travel Pouch', points: 6500, stock: 42, type: 'Merchandise', emoji: '🧳', color: 'sage' },
  { id: 3, name: 'Daily Reset Face Wash Duo', points: 4800, stock: 27, type: 'Groomix product', emoji: '🧴', color: 'blue' },
  { id: 4, name: 'Stainless Steel Water Bottle', points: 8500, stock: 9, type: 'Gift item', emoji: '💧', color: 'sand' },
];

export const payments = [
  { ref: 'PAY-8501', order: 'GR-24080', customer: 'The Daily Edit', date: '23 Nov 2026', amount: 21600, method: 'Bank transfer', status: 'Verified' },
  { ref: 'PAY-8500', order: 'GR-24081', customer: 'Aarav Wellness Mart', date: '24 Nov 2026', amount: 38400, method: 'UPI', status: 'Pending verification' },
  { ref: 'PAY-8498', order: 'GR-24077', customer: 'The Good Shelf', date: '20 Nov 2026', amount: 28800, method: 'Bank transfer', status: 'Verified' },
  { ref: 'PAY-8492', order: 'GR-24076', customer: 'Aarav Wellness Mart', date: '18 Nov 2026', amount: 19200, method: 'UPI', status: 'Refunded' },
];

export const returns = [
  { id: 'RET-1024', order: 'GR-24078', customer: 'Glow & Go Retail', date: '23 Nov 2026', item: 'Daily Strength Shampoo · 2 boxes', reason: 'Outer cartons damaged', status: 'Needs inspection' },
  { id: 'RET-1023', order: 'GR-24074', customer: 'The Daily Edit', date: '21 Nov 2026', item: 'Sunveil SPF 50 · 1 box', reason: 'Incorrect item received', status: 'Approved' },
  { id: 'RET-1022', order: 'GR-24070', customer: 'Aarav Wellness Mart', date: '19 Nov 2026', item: 'Cloudsoft Daily Moisturizer · 1 box', reason: 'Two units were leaking', status: 'Inspected' },
];

export const monthlySales = [
  { month: 'Jun', value: 38 }, { month: 'Jul', value: 54 }, { month: 'Aug', value: 46 },
  { month: 'Sep', value: 70 }, { month: 'Oct', value: 61 }, { month: 'Nov', value: 86 },
];
