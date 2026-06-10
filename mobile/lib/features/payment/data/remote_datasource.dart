import '../../../core/network/dio_client.dart';
import '../../../core/errors/exceptions.dart';
import 'models/payment_model.dart';

class PaymentRemoteDatasource {
  final DioClient client;
  const PaymentRemoteDatasource({required this.client});

  Future<PaymentModel> initiatePayment({
    required String dossierId,
    required String method,
    required String phone,
  }) async {
    final res = await client.post('/payment/initiate', data: {
      'dossier_id': dossierId,
      'method': method,
      'phone': phone,
    });
    if ((res.statusCode == 200 || res.statusCode == 201) && res.data != null) {
      return PaymentModel.fromJson(res.data as Map<String, dynamic>);
    }
    throw ApiException(
      message: 'Le paiement a échoué. Vérifiez votre solde.',
      statusCode: res.statusCode,
    );
  }
}
