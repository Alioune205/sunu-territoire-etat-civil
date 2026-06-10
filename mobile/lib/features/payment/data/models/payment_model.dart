class PaymentModel {
  final bool success;
  final String? receipt;
  final String? transactionId;

  const PaymentModel({
    required this.success,
    this.receipt,
    this.transactionId,
  });

  factory PaymentModel.fromJson(Map<String, dynamic> json) => PaymentModel(
        success: json['success'] as bool? ?? false,
        receipt: json['receipt'] as String?,
        transactionId: json['transaction_id'] as String?,
      );
}
