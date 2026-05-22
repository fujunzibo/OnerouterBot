import { ShoppingCart, Zap, Star, Lock, Clock } from 'lucide-react'

function ProductCard({ product, stock, onAddToCart, onBuyNow }) {
  const isOutOfStock = stock === 0

  return (
    <div className={`product-card ${isOutOfStock ? 'out-of-stock' : ''}`}>
      <div className="product-image-wrapper">
        <img 
          src={product.image} 
          alt={product.name}
          className="product-image"
        />
        {isOutOfStock && (
          <div className="out-of-stock-overlay">
            <span>Out of Stock</span>
          </div>
        )}
        {stock > 0 && stock <= 3 && (
          <div className="low-stock-badge">
            Only {stock} left!
          </div>
        )}
      </div>

      <div className="product-info">
        <div className="product-rating">
          <Star fill="#fbbf24" color="#fbbf24" size={16} />
          <span>4.9</span>
        </div>
        
        <h3 className="product-name">{product.name}</h3>
        <p className="product-description">{product.description}</p>

        <div className="product-features">
          {product.features.slice(0, 3).map((feature, index) => (
            <div key={index} className="feature-tag">
              {index === 0 && <Zap size={12} />}
              {index === 1 && <Lock size={12} />}
              {index === 2 && <Clock size={12} />}
              <span>{feature}</span>
            </div>
          ))}
        </div>

        <div className="product-price">
          <span className="price-currency">USD</span>
          <span className="price-amount">{product.price}</span>
          <span className="price-label">per card</span>
        </div>

        <div className="product-actions">
          <button 
            className="btn btn-secondary"
            onClick={onAddToCart}
            disabled={isOutOfStock}
          >
            <ShoppingCart size={18} />
            <span>Add to Cart</span>
          </button>
          <button 
            className="btn btn-primary"
            onClick={onBuyNow}
            disabled={isOutOfStock}
          >
            <Zap size={18} />
            <span>Buy Now</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ProductCard