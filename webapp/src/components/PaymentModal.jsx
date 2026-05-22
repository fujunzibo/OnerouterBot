import { X, CreditCard, Wallet, Coins, CheckCircle } from 'lucide-react'

function PaymentModal({ show, onClose, onPayment, total }) {
  if (!show) return null

  const paymentMethods = [
    {
      id: 'telegram-pay',
      name: 'Telegram Wallet Pay',
      description: 'Pay with your Telegram Wallet',
      icon: Wallet,
      color: '#229ED9'
    },
    {
      id: 'crypto',
      name: 'Crypto (USDT/TRC20)',
      description: 'Pay with USDT on TRC20 network',
      icon: Coins,
      color: '#32C5FF'
    },
    {
      id: 'card',
      name: 'Credit/Debit Card',
      description: 'Visa, Mastercard, American Express',
      icon: CreditCard,
      color: '#4CAF50'
    }
  ]

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Select Payment Method</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="payment-summary">
          <div className="summary-item">
            <span>Order Total:</span>
            <span className="summary-value">${total}</span>
          </div>
          <div className="summary-item">
            <span>Payment Method:</span>
            <span className="summary-value">Select below</span>
          </div>
        </div>

        <div className="payment-methods">
          {paymentMethods.map(method => {
            const Icon = method.icon
            return (
              <button
                key={method.id}
                className="payment-method-btn"
                onClick={() => onPayment(method.id)}
                style={{ '--accent-color': method.color }}
              >
                <div className="payment-icon" style={{ backgroundColor: method.color }}>
                  <Icon size={24} />
                </div>
                <div className="payment-info">
                  <h3>{method.name}</h3>
                  <p>{method.description}</p>
                </div>
                <div className="payment-check">
                  <CheckCircle size={20} />
                </div>
              </button>
            )
          })}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary btn-full" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default PaymentModal