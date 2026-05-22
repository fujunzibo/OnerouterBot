import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import Header from './components/Header'
import ProductCard from './components/ProductCard'
import Cart from './components/Cart'
import PaymentModal from './components/PaymentModal'
import OrderSuccess from './components/OrderSuccess'

const products = [
  {
    id: '10usd',
    name: 'Premium Card $10',
    faceValue: 10,
    price: 10,
    currency: 'USD',
    description: 'High-quality digital gift card',
    features: ['Instant delivery', 'Global use', 'No expiration'],
    image: 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=premium%20gold%20gift%20card%20with%20dollar%20sign%20elegant%20design&image_size=square'
  },
  {
    id: '25usd',
    name: 'Pro Card $25',
    faceValue: 25,
    price: 25,
    currency: 'USD',
    description: 'Professional-grade digital card',
    features: ['Instant delivery', 'Global use', 'No expiration', 'Priority support'],
    image: 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=professional%20silver%20gift%20card%20premium%20design&image_size=square'
  },
  {
    id: '50usd',
    name: 'Elite Card $50',
    faceValue: 50,
    price: 50,
    currency: 'USD',
    description: 'Ultimate digital gift card',
    features: ['Instant delivery', 'Global use', 'No expiration', 'VIP support', 'Bonus points'],
    image: 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=elite%20diamond%20gift%20card%20luxury%20golden%20design&image_size=square'
  },
  {
    id: '100usd',
    name: 'VIP Card $100',
    faceValue: 100,
    price: 100,
    currency: 'USD',
    description: 'Premium VIP digital card',
    features: ['Instant delivery', 'Global use', 'No expiration', '24/7 VIP support', 'Bonus points', 'Exclusive offers'],
    image: 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=vip%20platinum%20gift%20card%20luxury%20diamond%20design&image_size=square'
  }
]

function App() {
  const [cart, setCart] = useState([])
  const [stock, setStock] = useState({})
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [orderInfo, setOrderInfo] = useState(null)
  const [telegramData, setTelegramData] = useState(null)

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.ready()
      tg.expand()
      setTelegramData({
        user: tg.initDataUnsafe?.user,
        queryId: tg.initDataUnsafe?.query_id
      })
    }
    fetchStock()
  }, [])

  const fetchStock = async () => {
    try {
      const response = await axios.get('/api/stock')
      setStock(response.data)
    } catch (error) {
      console.error('Failed to fetch stock:', error)
    }
  }

  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id)
      if (existing) {
        return prev.map(item =>
          item.id === product.id
            ? { ...item, quantity: Math.min(item.quantity + 1, stock[product.id] || 99) }
            : item
        )
      }
      return [...prev, { ...product, quantity: 1 }]
    })
  }

  const removeFromCart = (productId) => {
    setCart(prev => prev.filter(item => item.id !== productId))
  }

  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId)
      return
    }
    setCart(prev => prev.map(item =>
      item.id === productId
        ? { ...item, quantity: Math.min(quantity, stock[item.id] || 99) }
        : item
    ))
  }

  const getTotal = () => {
    return cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
  }

  const handleBuyNow = (product) => {
    setSelectedProduct(product)
    setShowPaymentModal(true)
  }

  const handleCheckout = () => {
    if (cart.length === 0) return
    setSelectedProduct({
      id: 'cart',
      name: 'Bundle Purchase',
      price: getTotal(),
      currency: 'USD'
    })
    setShowPaymentModal(true)
  }

  const handlePayment = async (method) => {
    try {
      const orderData = {
        items: cart.length > 0 ? cart : [{ ...selectedProduct, quantity: 1 }],
        total: cart.length > 0 ? getTotal() : selectedProduct.price,
        currency: 'USD',
        paymentMethod: method,
        telegramData: telegramData
      }
      
      const response = await axios.post('/api/create-order', orderData)
      setOrderInfo(response.data)
      setShowPaymentModal(false)
      setShowSuccess(true)
      setCart([])
      fetchStock()
    } catch (error) {
      console.error('Payment failed:', error)
      alert('Payment failed, please try again')
    }
  }

  const handleCloseSuccess = () => {
    setShowSuccess(false)
    setOrderInfo(null)
  }

  return (
    <div className="app">
      <Header cartCount={cart.reduce((sum, item) => sum + item.quantity, 0)} onCheckout={handleCheckout} />
      
      <main className="main-content">
        <section className="hero">
          <h1>Welcome to Card Store</h1>
          <p>Discover premium digital gift cards at unbeatable prices</p>
        </section>

        <section className="products-section">
          <h2>Available Cards</h2>
          <div className="products-grid">
            {products.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                stock={stock[product.id] || 0}
                onAddToCart={() => addToCart(product)}
                onBuyNow={() => handleBuyNow(product)}
              />
            ))}
          </div>
        </section>
      </main>

      <Cart
        cart={cart}
        stock={stock}
        onUpdateQuantity={updateQuantity}
        onRemove={removeFromCart}
        onCheckout={handleCheckout}
        total={getTotal()}
      />

      <PaymentModal
        show={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        onPayment={handlePayment}
        total={cart.length > 0 ? getTotal() : selectedProduct?.price}
      />

      <OrderSuccess
        show={showSuccess}
        orderInfo={orderInfo}
        onClose={handleCloseSuccess}
      />
    </div>
  )
}

export default App