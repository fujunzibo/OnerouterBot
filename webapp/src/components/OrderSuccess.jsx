import { CheckCircle, Package, Copy, X } from 'lucide-react'
import { useState } from 'react'

function OrderSuccess({ show, orderInfo, onClose }) {
  const [copied, setCopied] = useState(false)

  if (!show || !orderInfo) return null

  const handleCopy = async () => {
    if (orderInfo.tokens && orderInfo.tokens.length > 0) {
      const tokensText = orderInfo.tokens.join('\n')
      await navigator.clipboard.writeText(tokensText)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="success-modal" onClick={e => e.stopPropagation()}>
        <div className="success-icon">
          <CheckCircle size={64} />
        </div>
        
        <h2>Order Successful!</h2>
        <p className="success-message">Thank you for your purchase. Your digital cards have been delivered.</p>

        <div className="order-details">
          <div className="detail-item">
            <span className="detail-label">Order ID:</span>
            <span className="detail-value">{orderInfo.orderId}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Amount:</span>
            <span className="detail-value">${orderInfo.total}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Payment Method:</span>
            <span className="detail-value">{orderInfo.paymentMethod}</span>
          </div>
        </div>

        {orderInfo.tokens && orderInfo.tokens.length > 0 && (
          <div className="tokens-section">
            <div className="tokens-header">
              <Package size={20} />
              <span>Your Cards</span>
              <button 
                className="copy-btn"
                onClick={handleCopy}
                title="Copy all tokens"
              >
                <Copy size={16} />
                <span>{copied ? 'Copied!' : 'Copy'}</span>
              </button>
            </div>
            <div className="tokens-list">
              {orderInfo.tokens.map((token, index) => (
                <div key={index} className="token-item">
                  <span className="token-index">{index + 1}</span>
                  <span className="token-value">{token}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="success-footer">
          <button className="btn btn-primary btn-full" onClick={onClose}>
            Continue Shopping
          </button>
        </div>

        <button className="close-btn close-top-right" onClick={onClose}>
          <X size={20} />
        </button>
      </div>
    </div>
  )
}

export default OrderSuccess