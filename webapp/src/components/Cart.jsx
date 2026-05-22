import { ShoppingCart, Minus, Plus, Trash2, X } from 'lucide-react'
import { useState } from 'react'

function Cart({ cart, stock, onUpdateQuantity, onRemove, onCheckout, total }) {
  const [isOpen, setIsOpen] = useState(false)

  if (cart.length === 0) {
    return null
  }

  return (
    <>
      <button 
        className="cart-toggle-btn"
        onClick={() => setIsOpen(true)}
      >
        <ShoppingCart size={24} />
        <span className="cart-count">{cart.reduce((sum, item) => sum + item.quantity, 0)}</span>
      </button>

      <div className={`cart-overlay ${isOpen ? 'open' : ''}`} onClick={() => setIsOpen(false)}>
        <div className="cart-drawer" onClick={e => e.stopPropagation()}>
          <div className="cart-header">
            <h2>Your Cart</h2>
            <button className="close-btn" onClick={() => setIsOpen(false)}>
              <X size={20} />
            </button>
          </div>

          <div className="cart-items">
            {cart.map(item => (
              <div key={item.id} className="cart-item">
                <img 
                  src={item.image} 
                  alt={item.name}
                  className="cart-item-image"
                />
                <div className="cart-item-info">
                  <h3>{item.name}</h3>
                  <p className="cart-item-price">${item.price}</p>
                  <p className="cart-item-stock">Stock: {stock[item.faceValue] || 0}</p>
                </div>
                <div className="cart-item-actions">
                  <button 
                    className="qty-btn"
                    onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
                  >
                    <Minus size={16} />
                  </button>
                  <span className="qty-value">{item.quantity}</span>
                  <button 
                    className="qty-btn"
                    onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
                  >
                    <Plus size={16} />
                  </button>
                  <button 
                    className="remove-btn"
                    onClick={() => onRemove(item.id)}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="cart-footer">
            <div className="cart-total">
              <span>Total:</span>
              <span className="total-amount">${total}</span>
            </div>
            <button 
              className="btn btn-primary btn-full"
              onClick={() => {
                onCheckout()
                setIsOpen(false)
              }}
            >
              Proceed to Payment
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

export default Cart